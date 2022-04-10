### VoiceComp
An application for conducting voice comparison experiments.
It provides user interface for controlling several aspects of an experiment such as configuring the experiment setup, conducting the experiment, data collection, data analysis. 
The tool is implemented with HTML, CSS, JavaScript and jQuery for front-end interface, and Python (Django) for back-end.
### How to Use?
For each trial, two speech samples at a time are presented to the user to listen to. 
Participants can play and pause either sample, before confirming their decisions. 
Before confirming their decision, the participant may also provide how confident they are on their choice.
When both the decision and the confidence level are submitted, the ’next’ button will be enabled for next trials.

### Basic Configuration Controls
Admins can configure the experiments by logging in through the interface. 
#####  Instructions
A short instructions for participants to proceed the experiment.

#####  Decision Option
Configure the options to be presented for the particiants along with the points/score awarded for each option.

#####  Audio files
Set up a list of audio files along with options such as randomize the order or set a sequence.

### For Developers:

#####  Configure the experiment options
Change these settings in settings.py file when required.
- GAMIFIED = 'true' (To enable gamified version of the experiment. Other option 'false')
- ENABLE_LIFE = 'true' (To enable restriction ending the experiment after certain wrong attempt. Other option 'false')
- TOTAL_LIFE = 5 (Number of max wrong attempt allowed if ENABLE_LIFE='true'. Accepted values - positive integer number)
- MAX_LEVEL = 3 (Maximum number of level per game if GAMIFIED='true'. Accepted values - positive integer number)
- TOTALTRIALS_PER_LEVEL = 10 (Total number of trials in each level if GAMIFIED='true'. Accepted values - positive integer number)
- THEME = 'dark' (default theme for experiment. Other option 'light')

#####  Locally running the application for debugging

1. Install python in local machine and clone this repository.
2. Create virtual environment in the root directory VoiceComp.
> python -m venv venv
3. Activate virtual environment.
> venv/Scripts/activate
4. Install requirements.
> pip install -r requirements.txt
5. Migrate database.
> python manage.py makemigrations menu
> python manage.py migrate menu

6. Collect static files.
> python manage.py collectstatic

7. Copy all the required audio files (.wav) inside /media/voicedata/wav directory
8. Edit settings.py file. Set DEBUG=True and URL='http://localhost:8000/'
9. Run the application in port 8000.
> python manage.py runserver 0.0.0.0:8000
10. Access from web browser with url, 'http://localhost:8000/'



