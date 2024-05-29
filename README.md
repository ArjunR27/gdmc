This is a project in CSC-480 at Cal Poly SLO under Prof. Rodrigp Cannan. 

Report uploaded under "GDMC_Final_Report.pdf"

Credit:
- Utilizes GDPC (Generative Design Python Client) and GDMC-HTTP frameworks
- GDPC GitHub: https://github.com/avdstaaij/gdpc
- GDMC-HTTP GitHub: https://github.com/Niels-NTG/gdmc_http_interface


Installing Dependencies:
1) GDPC Dependencies:
    - python3 -m pip install gdpc
 
2) GDMC-HTTP Dependencies:
    - Download Forge Mod Installer
    -  Download mod's jar file linked in GitHub and move it into the mod folder
    - Open Minecraft launcher and click "Play" on the Forge installation in the list



How to Run our Project:
1) Create a minecraft world connected via local host using the http interface
2) Pick a location within the world and set the build area within the world using the /setbuildarea command
3) To run our script, within the command line run the command: "python main.py"
4) This will run the main script and executes the generative design model
