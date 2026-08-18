#!/usr/bin/env bash
set -euo pipefail

VERSION="${VERSION:-0.1.0}"
ARCH="${ARCH:-amd64}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_ROOT="$ROOT/build/deb"
PACKAGE_ROOT="$BUILD_ROOT/mastermind_${VERSION}_${ARCH}"
OUTPUT="$ROOT/dist/mastermind_${VERSION}_${ARCH}.deb"

cd "$ROOT"
rm -rf "$BUILD_ROOT" "$ROOT/build/mastermind" "$ROOT/dist/mastermind"
mkdir -p "$ROOT/dist"

python3 -m PyInstaller --clean --noconfirm mastermind.spec

mkdir -p \
    "$PACKAGE_ROOT/DEBIAN" \
    "$PACKAGE_ROOT/usr/bin" \
    "$PACKAGE_ROOT/usr/share/applications" \
    "$PACKAGE_ROOT/usr/share/icons/hicolor/scalable/apps" \
    "$PACKAGE_ROOT/usr/share/doc/mastermind"

install -m 0755 "$ROOT/dist/mastermind" "$PACKAGE_ROOT/usr/bin/mastermind"
install -m 0644 "$ROOT/packaging/mastermind.desktop" "$PACKAGE_ROOT/usr/share/applications/mastermind.desktop"
install -m 0644 "$ROOT/static/mastermind.svg" "$PACKAGE_ROOT/usr/share/icons/hicolor/scalable/apps/mastermind.svg"
install -m 0644 "$ROOT/README.md" "$PACKAGE_ROOT/usr/share/doc/mastermind/README.md"

cat > "$PACKAGE_ROOT/DEBIAN/control" <<EOF
Package: mastermind
Version: $VERSION
Section: games
Priority: optional
Architecture: $ARCH
Maintainer: Guillaume Boileau <guillaume.boileaupro@gmail.com>
Depends: libc6 (>= 2.31), libgl1, libegl1, libxkbcommon-x11-0, libxcb-cursor0
Description: Mastermind desktop pour Ubuntu
 Jeu de logique Mastermind avec modes couleurs et chiffres, score,
 chronometre et historique local persistant.
EOF

dpkg-deb --build --root-owner-group "$PACKAGE_ROOT" "$OUTPUT"
echo "$OUTPUT"
