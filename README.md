# Photobooth-Website
A website that allows users to take photobooth images, choose a frame and filter, design the strip with AI frame design, download the strip, and print the strip


⋆˚꩜｡ Features :

- Live Webcam Capture : taking a series of photos directly in the browswer using your device!
- Frame Size : choose from 5 different frame sizes.
- Frame Design : an AI feature that generates a frame design based on user input
- Filter : apply fun filters to your photos!
- Download your strip : export your finished strip as high-quality PNG image ready to share and print.
- Print your strip : exports you finished strip onto a 4x6 image and redirects you to the CVS Photos webpage so you can print a physical copy

# Demo
- https://youtu.be/sYqQGZQB3Uk?si=Biri4ezuwJYDcXxq

# Tech Stack

| Layer    | Technology      |
|----------|-----------------|
| Backend  | Python (Flask)  |
| Frontend | HTML, CSS       |
| Data     | CSV (usage log) |
| API Key  | Google Gemini   |


## Installation

1. Clone the repository
   - git clone https://github.com/Ohio-University-CS/Photobooth-website.git
   - cd Photobooth-website

2. Install the dependencies   
   - python3 -m venv venv
   - source venv/bin/activate
   - pip install flask
   - pip install -r requirements.txt

3. Run the applications
   - python main.py

4. Open in your browser
   - http://localhost:5001

> ( ˶°ㅁ°) !! The app requires camera permission. So make sure your browser allows webcam access for localhost.

# Bugs and Known Issues
- Our actual webpage hasn't updated with our current state of the project
- Some of the spacing is off on our UI
- Our API key can only handle 15 calls per hour, so the AI frames can only be generated 15 times an hour
- Our AI cannot handle complex design ideas, only simple designs

# Future
- We would like to get a better webpage working that isn't just a local host and not as buggy
- We would like to add a sticker feature so users can design their strips with stickers as well
- Potentially, we may add a login feature where it saves previous photostrips done by the user

## Project structure

```
Photobooth-website/
├── main.py           # Runs the main program and moves from page to page                  
├── stripselect.py    # All the data saving aspects of the program
├── static/           # CSS, JS, images, frames
├── templates/        # HTML templates
├── data/
│   └── log.csv           # Usage log (auto-generated, not tracked in git)
├── test ./           # Test files
└── README.md
```

## GitHub Release

 (ദ്ദി˙ᗜ˙) this would be our first release 'v1.0.0'. 
  - Source code
  - Release notes.

## Contributors:

| Name | GitHub |
|------|--------|
| Annie Nguyen | [@habitzs](https://github.com/habitzs) |
| Katrin Williams | [@kcwilliams22](https://github.com/kcwilliams22) |
| Sarah Ivey | [@iveysarah](https://github.com/iveysarah) |
| Will Kashner | [@Will-56](https://github.com/Will-56) |





