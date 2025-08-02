---
title: "COMP322 Final Project Reflection"
date: "2024-12-14"
authors:
  - "Eric Spencer"
  - "Matthew Caballero"
draft: false
image: "/previews/healthup!.png"
tags: ["React Native"]
---

_Eric Spencer + Matthew Caballero_  
_December 14, 2024_  
_COMP 322/422 Reflection_

# Reflections on HealthUp!

## Abstract

HealthUp! is an application focused on bettering a user’s information about their health. Users can log nutritional information of foods and track their workouts. We wanted to develop this app to support our passion for healthy living.

## Repository (without keys)

[GitHub Repository](https://github.com/EricSpencer00/HealthUp-)

*If you attempt to download and run the app, see the bolded text in “Testing & Iterative Design.” The iOS version of the app does not work.*

- **Mid-Project Demo:** [YouTube Short](https://youtube.com/shorts/W9zFw_DEovk?si=WDZh0-gq7Xn4-bH2)
- **Final-Project Demo:** [YouTube Short](https://youtube.com/shorts/P4aK_aXt1Gk?si=4_iR_fdqSYEZ1HSh)

[Repeated Links:]  
[GitHub Repository](https://github.com/EricSpencer00/HealthUp-)  
[Mid-Project Demo](https://youtube.com/shorts/W9zFw_DEovk?si=WDZh0-gq7Xn4-bH2)  
[Final-Project Demo](https://youtube.com/shorts/P4aK_aXt1Gk?si=4_iR_fdqSYEZ1HSh)

## Final Presentation

_C322 Fit Slides_

## Table of Contents

1. Title & Abstract  
2. Table of Contents  
3. Project Participants  
4. Project Narrative  
   - Original Project Idea  
   - Inspiration  
5. Initial UI Concepts  
   - Navigation Hierarchy  
6. Design Specifications  
7. Testing & Iterative Design  
8. Screenshots Throughout Development  
9. Roadblocks  
10. Conclusion  

[Presentation Slides](https://docs.google.com/presentation/d/1yi1cYk8q-VXpG3qnEf6VLfvc2WavrzsmRZ5YF6c5o_g/edit?usp=sharing)

## Project Participants

### Eric Spencer
- **Commits:** 82  
- **Additions:** 58,800  
- **Deletions:** 38,916  

**Key Contributions:**
- NutritionScreen.js  
- Barcode Scanner  
- API usages  

**Worked on:**
- Presentations  
- Npm dependencies  
- Trying to get the app to compile with npm dependencies  
- User Context  
- FitnessScreen.js  
- HomeScreen.js  
- MainTabs.js (removed)  
- NutritionScreen.js  
- JournalScreen.js  
- User.js (not used)  
- UserContext.js  
- UserInfoScreen.js  
- UserSettingsScreen.js (removed)

### Matthew Caballero
- **Commits:** 22  
- **Additions:** 2,466  
- **Deletions:** 526  

**Key Contributions:**
- CurrentWorkoutScreen.js  
- UserSettingsScreen.js  
- WorkoutDiary.js  
- Firebase integration  
- UI layout design & implementation  

**Worked on:**
- Presentations  
- Npm dependencies  
- Exercises transferring between screens

## Project Narrative

Our goal is to simplify the experience of people trying to improve their physical health. Both of us find that being fit is a great contributor to living a long happy life. Through this app, we want to support users’ efforts in being more aware of what they are eating with a macronutrient tracker. Users can also scan barcodes using their camera to get nutritional information of the product, which gets added to the tracker. Another aspect of healthy living is exercising, and our workout diary can assist our users by keeping track of their sets and reps for each exercise. Users will also be able to create a workout from a list of recommended exercises.

### Original Project Idea

A user signs in with their email and gets assigned a UserID. Then, any actions performed in the app are correlated with that user in the FireBase DB. This allows data to exist on different logins on different devices. Once a user signs in, they are met with 3 options—Nutrition, Workouts, and Journal. The first two buttons allow you to write to the third option, the Journal. When you add a Workout or a Food/Nutrition entry, it gets updated to the journal to be tracked by the user. The user is supposed to be able to see their email and who they are signed in as. Within each screen there are various actions you are able to take.

### Inspiration

MyFitnessPal requires a subscription to use the barcode feature. Why not make it ourselves for free? Matt had ideas of creating a workout app, so we combined our ideas to create HealthUp!

## Initial UI Concepts

### Navigation Hierarchy

**[Insert Navigation Hierarchy image here]**

## Design Specifications

- **WelcomeScreen.js:** View the title of the app, and navigate to the sign in screen.  
- **SignInScreen.js:** Log in or sign up here and navigate to the app’s home screen after a successful login.  
- **HomeScreen.js:** Contains navigation options to the nutrition screen, the workout screen, the journal screen, or the profile screen.  
- **NutritionScreen.js and /Barcode:** Search for a specific food; if you want to add it to your journal, press the button to log the time and nutrients of the food in your journal. Alternatively, scan a barcode to automatically search for a food.  
- **WorkoutScreen.js in /WorkoutDiary:** Search for workouts after navigating to the fitness screen, or enter your own. Once you have your list, you can workout by setting a timer within the app. You can switch between workouts in the CurrentWorkoutScreen.js.  
- **FitnessScreen.js:** If you are having trouble looking for exercises to do in your workout, you can search for exercises by muscle type.  
- **JournalScreen.js:** View your logged workouts and nutrition; it serves as a representation of most of your data in the database.  
- **UserInfoScreen.js/profile screen:** View different account information, such as username, email, and weight.

_Additional note:_ We kept a consistent minimal color scheme outside of the welcome and login screens, which allows the user to focus on logging their nutrition and exercises without being distracted by bright colors.

## Testing & Iterative Design

I’ll be speaking about the main branch of the repository since trying to figure out diverging branches (when they stopped being worked on) would have been too confusing. In one instance, the main branch overwrote the preceding branch because of bad Android/iOS files that differed significantly from an original “npm init app” setup. In early October, I nuked the branch with a new repo, while the barcode_working branch retains the original commit history.

I initiated a personal app project (which included mentions of “dailyTask”) that was later overwritten. Most commits were just attempts to get the app to compile on my emulator (which was really challenging). The real development began on October 4 with the birth of “comp322application.”

I dived into the Barcode functionality right away—this turned out to be a mistake for several reasons. The npm installations did not cooperate when trying to manage multiple packages simultaneously, likely due to my system’s configuration. Consequently, I spent about a month and a half debugging Android and iOS files instead of focusing on JavaScript. It was after Thanksgiving that I informed Matt that I needed to abandon the progress on the problematic branch and start fresh on the working branch.

**Key Technical Changes:**
- **gradle.properties:** Added `VisionCamera_enableCodeScanner=true`
- **AndroidManifest.xml:** Added the android permission for Camera and Record_audio (the latter being optional)
- Changed generated files in workspace.xml, deviceStreaming.xml, and vcs.xml (which may have contributed to build errors)
- Integrated a working BarcodeScanner.js (not just a simulated “type a barcode in” functionality)
- Added react-native-vision-camera to package.json

Subsequent commits were purely changes in JavaScript. The development process resembled three months of “light” work and one week of intense progress. When solving npm package issues, the final resolution often occurred at the very last minute.

The last working version on the main branch was just before the Barcode functionality was implemented. For instance, commit “12117df” compiles correctly while commit “f2c2812” fails. The solution required pulling the first commit, compiling the app, then pulling again and refreshing the JavaScript.

After commit “f2c2812,” changes included:
- Updating **gradle.properties** with `VisionCamera_enableCodeScanner=true`
- **AndroidManifest.xml:** Adding necessary permissions
- Modifying generated configuration files
- Integrating a functional BarcodeScanner.js
- Adding react-native-vision-camera to the package dependencies

Later commits continue the progression of the app’s development. It became evident that when you give yourself three months for a project, most of the work is done lightly until a final week of hard work. For an npm package to work flawlessly, the solution only emerged on the final day before it was due. Git errors (such as accidentally pushing node modules) and refreshing the JavaScript on the emulator were recurring challenges.

## Roadblocks

- There was supposed to be better data representation in JournalScreen.js.
- The timer was intended to support custom time input.
- I wanted to implement a custom workout list allowing users to select from lists like arms day or legs day, but this was not completed.
- The User Settings could have been enhanced to display more data.
- There is currently no way to stay signed into the app; you must log in each time.
- The only way to sign out of the app is to restart it.
- The app formerly featured MainTabs which allowed users to remain on one screen after logging in, but this was removed due to an npm package dependency.
- Barcode functionality depends on the data available in Nutritionix's database; for instance, a barcode on a European candy did not register.
- There was an intention to allow users to log their weight and height in User Settings to derive a more accurate DV% in NutritionScreen (by applying a multiplier based on the API call).

## Conclusion

This project was an excellent way to learn about React Native development in an academic environment. We also learned a lot about project management and meeting tight deadlines. Although a more refined timeline and additional effort in design and user experience would have been beneficial, we ultimately delivered a working app that fulfilled about 95% of our vision. Communication was essential throughout the project, ensuring that both team members stayed informed about ongoing work. This hands-on experience has undoubtedly prepared us for future collaborative programming endeavors.
