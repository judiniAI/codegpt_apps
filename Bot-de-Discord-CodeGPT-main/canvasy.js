const { createCanvas, loadImage, registerFont } = require('canvas');

async function createCompositeImage(profileImageUrl, memberCount, memberName) {
  try {
    // Load background and profile image from the provided URL
    const background = await loadImage('./img/background.png');
    const profileImage = await loadImage(profileImageUrl);

    // Set up a canvas matching the background size
    const canvas = createCanvas(background.width, background.height);
    const ctx = canvas.getContext('2d');

    // Draw the background image
    ctx.drawImage(background, 0, 0);

    // Resize and draw the profile image at the specified position
    const resizedWidth = canvas.width * 0.21;
    const resizedHeight = canvas.width * 0.21;
    const xPosition = (canvas.width - resizedWidth) / 2;
    const yPosition = (canvas.height - resizedHeight) / 2;

    // Add text with the member count, centered horizontally
    ctx.font = '100px sans-serif';  // Use the default sans-serif font
    ctx.font = ctx.font.replace('100px', 'bold 100px');  // Apply bold to the font
    ctx.fillStyle = 'white';

    // Measure the text width to calculate the horizontal center position
    const text = `${memberName}!`;
    const textWidth = ctx.measureText(text).width;
    const textXPosition = (canvas.width - textWidth) / 2;

    // Adjust the `y` position to be below the profile image
    const textYPosition = yPosition + resizedHeight + 150; // Adjust as needed for spacing

    // Draw the centered text
    ctx.fillText(text, textXPosition, textYPosition);

    // Adjust the yPosition to move the image and clipping path up
    const offsetY = 150; // Adjust this value to control the vertical position
    const adjustedYPosition = yPosition - offsetY;

    // Begin a new path to create a circular clipping area
    ctx.beginPath();
    ctx.arc(
      xPosition + resizedWidth / 2,  // x position of circle center
      adjustedYPosition + resizedHeight / 2, // y position of circle center
      resizedWidth / 2,              // radius (half the width of the image to make it a circle)
      0,
      Math.PI * 2
    );
    ctx.closePath();

    // Apply the clipping path
    ctx.clip();

    ctx.drawImage(profileImage, xPosition, adjustedYPosition, resizedWidth, resizedHeight);

    // Optionally, reset the clipping path after drawing
    ctx.restore();


    // Convert the canvas to a buffer and return it
    return canvas.toBuffer('image/jpeg');
  } catch (error) {
    console.error('Error creating image:', error);
  }
}

module.exports = { createCompositeImage };