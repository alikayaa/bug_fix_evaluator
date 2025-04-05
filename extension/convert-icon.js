const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

// Path to SVG and PNG files
const svgPath = path.join(__dirname, 'images', 'icon.svg');
const pngPath = path.join(__dirname, 'images', 'icon.png');

// Read SVG file
const svgBuffer = fs.readFileSync(svgPath);

// Convert SVG to PNG
sharp(svgBuffer)
  .resize(128, 128) // Resize to 128x128
  .png()
  .toFile(pngPath)
  .then(() => {
    console.log(`Successfully converted SVG to PNG: ${pngPath}`);
  })
  .catch(err => {
    console.error('Error converting SVG to PNG:', err);
  }); 