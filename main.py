
import os # OS module for file manipulation.
import wx # WxPython for the GUI.
import emoji # Emoji for file upload status.

# Various PyCryptodome functions
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class Application(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(600, 400)) # Set Size
        self.SetBackgroundColour(wx.Colour(240, 240, 240)) # Set background color
        self.CreateStatusBar() # Adds a status bar 
        
        # Initialize file_path as None (no file uploaded yet).
        self.file_path = None

        # Setting up the menu.
        filemenu = wx.Menu()
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " About the program.")
        menuExit = filemenu.Append(wx.ID_EXIT, "&Exit", " Close the program.")

        # Create the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&Menu")
        self.SetMenuBar(menuBar)

        # Buttons
        self.uploadFile = wx.Button(self, label="Upload File")
        self.encryptFile = wx.Button(self, label="Encrypt File")
        self.encryptFile.Disable()  # Disable until a file is uploaded
        self.decryptFile = wx.Button(self, label="Decrypt File")
        self.decryptFile.Disable() # Disable until a file is uploaded
        self.clearFile = wx.Button(self, label="Remove File")
        self.clearFile.Disable() # Disable until a file is uploaded

        # Label for uploaded file status
        self.uploadLabel = wx.StaticText(self, label=f"{emoji.emojize(':cross_mark:')}\t No File Uploaded", style=wx.ALIGN_LEFT)
        # Lavel for encrypt file
        self.encryptLabel = wx.StaticText(self, label=f"{emoji.emojize(':locked:')}", style=wx.ALIGN_LEFT)
        # Label for decrypt file
        self.decryptLabel = wx.StaticText(self, label=f"{emoji.emojize(':unlocked:')}", style=wx.ALIGN_LEFT)
        # Label for remove file
        self.removeLabel = wx.StaticText(self, label=f"{emoji.emojize(':wastebasket:')}", style=wx.ALIGN_LEFT)

        # Bind Events to various wx widgets.
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.uploadFile)
        self.Bind(wx.EVT_BUTTON, self.OnEncrypt, self.encryptFile)
        self.Bind(wx.EVT_BUTTON, self.OnDecrypt, self.decryptFile)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveFile, self.clearFile)

        # Layouts
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # Upload Row
        uploadLayout = wx.BoxSizer(wx.HORIZONTAL)
        uploadLayout.Add(self.uploadFile, 0, wx.ALL, 10)
        uploadLayout.Add(self.uploadLabel, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        mainSizer.Add(uploadLayout, 0, wx.EXPAND)

        # Encrypt Row
        encryptLayout = wx.BoxSizer(wx.HORIZONTAL)
        encryptLayout.Add(self.encryptFile, 0, wx.ALL, 10)
        encryptLayout.Add(self.encryptLabel, 1, wx.ALL, 10)
        mainSizer.Add(encryptLayout, 0, wx.EXPAND)

        # Decrypt Row - Add decryptFile button and decryptLabel together
        decryptLayout = wx.BoxSizer(wx.HORIZONTAL)
        decryptLayout.Add(self.decryptFile, 0, wx.ALL, 10)
        decryptLayout.Add(self.decryptLabel, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        mainSizer.Add(decryptLayout, 0, wx.EXPAND)

        # Clear Row - Add removeLabel next to the remove file button
        removeLayout = wx.BoxSizer(wx.HORIZONTAL)
        removeLayout.Add(self.clearFile, 0, wx.ALL, 10)
        removeLayout.Add(self.removeLabel, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        mainSizer.Add(removeLayout, 0, wx.EXPAND)

        # Initialise sizer and show application
        self.SetSizer(mainSizer)
        self.Layout()
        self.Show()

    # Function for opening file, searches OS File Explorer.
    def OnOpen(self, e):
        dlg = wx.FileDialog(self, "Choose a file", "", "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            self.file_path = os.path.join(dirname, filename) # Sets file path to directory + file name.
            self.uploadLabel.SetLabel(f"{emoji.emojize(':check_mark:')}\t{filename}") # Changes status.
            self.Layout() # Reset Layout
            self.encryptFile.Enable() 
            self.decryptFile.Enable()
            self.clearFile.Enable()
        dlg.Destroy()

    # Function for file encryption.
    def OnEncrypt(self, e):
        if self.file_path is None:
            wx.MessageBox("Please upload a file first!", "Error", wx.OK | wx.ICON_ERROR)
            return
        try:
             # Prompt for password using a secure input dialog
            dlg = wx.TextEntryDialog(
                self,
                message="Enter a password to encrypt the file:\n\nUse 12-20 characters." \
                "\nMix upper case, lower case, and symbols.\nExamples:\n- G7x$8mN@!f42Zp\n- Orange!Trampoline-96$Coffee" \
                "\n\nRemember it! Use a password manager.",
                caption="Password Required",
                style=wx.TE_PASSWORD | wx.OK | wx.CANCEL
            )
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return  # User cancelled encryption
            password = dlg.GetValue().encode()
            dlg.Destroy()
            # Read the content of the file
            with open(self.file_path, 'rb') as f:
                file_data = f.read()
            # Generate salt and derive AES key using PBKDF2
            salt = get_random_bytes(16)  # Save this for decryption
            key = PBKDF2(password, salt, dkLen=32, count=200_000) # 32 for AES-256
            # Create AES cipher in CBC mode
            cipher = AES.new(key, AES.MODE_CBC)
            iv = cipher.iv
            # Pad and encrypt data
            padded_data = pad(file_data, AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            # Save encrypted file with salt + IV prepended
            encrypted_file_path = self.file_path + ".encrypted"
            with open(encrypted_file_path, 'wb') as enc_file:
                enc_file.write(salt)      # 16 bytes
                enc_file.write(iv)        # 16 bytes
                enc_file.write(encrypted_data)
            # Success UI feedback
            self.encryptLabel.SetLabel(f"{emoji.emojize(':locked_with_key:')}\tFile encrypted successfully!")
            wx.MessageBox(f"File encrypted and saved as: {encrypted_file_path}", "Success", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"An error occurred during encryption: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    # Function for file decryption
    def OnDecrypt(self, e):
        if self.file_path is None:
            wx.MessageBox("Please upload a file first!", "Error", wx.OK | wx.ICON_ERROR)
            return
        try:
            # Prompt for password to decrypt the file.
            dlg = wx.TextEntryDialog(
                self,
                message="Enter the password to decrypt the file:\n\nYou must use the same password used for encryption.",
                caption="Password Required",
                style=wx.TE_PASSWORD | wx.OK | wx.CANCEL
            )
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return  # User cancelled decryption
            password = dlg.GetValue().encode()
            dlg.Destroy()
            # Read the encrypted file
            with open(self.file_path, 'rb') as enc_file:
                salt = enc_file.read(16)  # 16 bytes for salt
                iv = enc_file.read(16)    # 16 bytes for IV
                encrypted_data = enc_file.read()  # The rest is the encrypted data
            # Derive the key using PBKDF2 (same as in encryption)
            key = PBKDF2(password, salt, dkLen=32, count=200_000)
            # Initialize the AES cipher with the derived key and IV
            cipher = AES.new(key, AES.MODE_CBC, iv)
            # Decrypt the data
            decrypted_data = cipher.decrypt(encrypted_data)
            # Remove padding (PKCS7 padding)
            decrypted_data = unpad(decrypted_data, AES.block_size)
            # Save the decrypted file
            decrypted_file_path = self.file_path.replace('.encrypted', '.decrypted')
            with open(decrypted_file_path, 'wb') as dec_file:
                dec_file.write(decrypted_data)
            # Success UI feedback
            self.decryptLabel.SetLabel(f"{emoji.emojize(':unlocked:')}\tFile decrypted successfully!")
            wx.MessageBox(f"File decrypted and saved as: {decrypted_file_path}", "Success", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"An error occurred during decryption: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    # Function to remove the file.
    def OnRemoveFile(self, e):
        self.file_path = None  # Clear the file path
        self.uploadLabel.SetLabel(f"{emoji.emojize(':cross_mark:')}\t No File Uploaded")  # Reset upload status
        self.Layout() # Reset layout
        self.encryptFile.Disable()  # Disable the encrypt button since no file is attached
        self.decryptFile.Disable()  # Disable the decrypt button
        self.clearFile.Disable()  # Disable the remove button once file is removed
        wx.MessageBox("File removed successfully.", "Success", wx.OK | wx.ICON_INFORMATION)

    # Function for 'about', opens a dialog box with info.
    def OnAbout(self, e):
        dialog = wx.MessageDialog(self, "This is a file encryption tool that uses AES-256.\n" \
        "AES divides the entirety of your file into 32 bytes, it applies several iterations of mathematical " \
        "transformations to those 32 bytes, completely changing the original file, and hiding the file data.")
        dialog.ShowModal()
        dialog.Destroy()

    # Function for 'exit', closes the app.
    def OnExit(self, e):
        self.Close(True)

app = wx.App(False)
frame = Application(None, 'AES-256 File Encryption with WxPython')
app.MainLoop()