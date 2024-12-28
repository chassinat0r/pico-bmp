from test_waveshare_pico_LCD_35 import LCD_3inch5

# Custom error for if the specified bitmap file isn't found
class FileNotFoundError(Exception):
    pass

'''
Bitmap Manager class
- decode: Decodes bitmaps and stores them under a given name
- to_rgb565: Converts RGB888 to RGB565 to work on display
- render: Render decoded bitmaps at a given postion on the screen
and scale
'''

class BitmapManager():
    def __init__(self):
        self.bitmaps = {} # Create empty dictionary to store decoded BMPs
    
    # Function to convert RGB888 to RGB565
    def to_rgb565(self, R, G, B):
        # I copied this function after hours of trying to fix colours; I have no idea how it works
        # and don't want to lose my sanity finding out
        return (((G&0b00011100)<<3) +((B&0b11111000)>>3)<<8) + (R&0b11111000)+((G&0b11100000)>>5)

    # Function to decode a bitmap file into rows and columns, and store it under a name in the dictionary
    def decode(self, path, name):
        try:
            f = open(path, "rb") # Attempt to open the file
        except OSError: # An error occurred trying to open it
            raise FileNotFoundError("File does not exist") # More specific
        
        data = f.read() # Read contents of file
        
        f.close() # Close file as we don't need it anymore
        
        # Verify the file is a bitmap
        signature = data[0:2] # Get the first two bytes in the file; this is the length of the signature for BMP
        
        if signature != b"BM": # If signature is not "BM", that of a bitmap
            raise ValueError("File is not a bitmap image") # Throw error
        
        pixels_start = data[10] # Byte 10 gives the byte in the file where the pixels of the image start
    
        width = data[18] # Get width at byte 18
        height = data[22] # Get height at byte 22
    
        row = []
        image = [] # Array containing rows of pixels of the image
    
        # Iterate through each pixel from the start of pixels until the end of the file, going up by 4 as each pixel = 4 bytes
        for i in range(pixels_start, len(data), 4):
            # Convert BGR888 (for some reason the colours in Bitmap are BGR not RGB) to RGB565
            # Append to row
            row.append(self.to_rgb565(data[i+2], data[i+1], data[i])) 
            if len(row) == width: # If the length of the row is equal to the width, meaning the row is full
                image.append(row) # Append row to the image array
                row = [] # Empty row to move onto the next row
                
        self.bitmaps[name] = image # Store the decoded image under the given name in the bitmaps dictionary
        

    # Function to render a stored decoded bitmap onto the LCD at a given position and scale
    def render(self, LCD, name, start_x = 0, start_y = 0, scale = 1):
        try:
            image = self.bitmaps[name] # Get image corresponding to name
        except KeyError:
            raise ValueError(name + " is not the name of a decoded bitmap\nCheck the name and make sure you have decoded the bitmap first.") # Throw error

        # Go through and render each pixel in the image at the given X, Y, and scale
        for y in range(0, len(image)): # Iterate through each row in the image
            row = image[y] # Get row
            for x in range(0, len(row)): # Iterate through each column in the row
                pixel = row[x] # Get pixel
                
                # Draw rectangle for the pixel
                LCD.fill_rect(start_x + x*scale, start_y + (len(image)-1-y)*scale, scale, scale, pixel) 
        
        LCD.show_up() # Display on top third of display

if __name__ == "__main__": # Demo
    LCD = LCD_3inch5() # Initialise LCD
    LCD.bl_ctrl(100)

    LCD.fill(LCD.BLACK) # Black background
    # Apply to all thirds of LCD
    LCD.show_up()
    LCD.show_mid()
    LCD.show_down()

    bmp_mgr = BitmapManager() # Create bitmap manager
    bmp_mgr.decode("win95.bmp", "win95") # Decode Windows 95 logo and store under name "win95"
    bmp_mgr.decode("creeper.bmp", "creeper") # Decode Minecraft creeper face and store under name "creeper"

    bmp_mgr.render(LCD, "win95") # Render "win95" at default position X: 0, Y: 0 with no scaling (1 pixel per pixel)
    bmp_mgr.render(LCD, "creeper", 130, 10, 10) # Render "creeper" at X: 130, Y: 10 with 10x scaling (10 pixels per pixel)

