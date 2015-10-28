# HRV
Research Project on Heart Rate Variability - DTU 2015

For more information, visit: http://hrv.luanca.eu/

## Contents

### Android Application

Takes raw data from Zephyr HxM and exports as a file. Requires that you add your own google maps key in order to get it to work.

### Python script

Takes the file and exports a file that can be used by gHRV. Requires that you change the file paths in the class to your particular need.

## How to use

### Before work
1. Get a Zephyr HxM.
2. Load Android App on Android Studio
3. Add your own google maps key
4. Install app on your phone
5. Pair your phone with the HxM

### During the testing
6. Open the app
7. Put the HxM on
8. Press the heart button
9. If the connecting didn't work, press the refresh button.
10. If you are not receiving any HR data, but do receive other data such as distance, try taking the HxM off and putting it back on repeatedly until the data shows.
11. Once you see that data is coming in, press the record
12. Let it run for a few minutes before and after your testing
13. Once you are done, press the record button again to stop recording.

### After testing
14. File should be saved in your Downloads folder
15. Use the python script to create a file that can be loaded into gHRV
16. We advice that you keep the original, as it records a lot of other data.
17. The log should display any abnormalities such as packages received twice or skipped beats. The code fixes all of these.
18. The log also shows if there are any "abnormal" beats (as in very fast or slow) but still exports them.

### HRV
19. Load the file in gHRV and have fun.
20. For more info read the gHRV documentation
