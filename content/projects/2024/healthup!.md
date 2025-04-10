
+++
title = "HealthUp! - iOS/Android Application"
date = "2024-12-14"
description = "COMP 322/422 Reflection for HealthUp! project by Eric Spencer and Matthew Caballero."
categories = ["Mobile", "React Native", "Fitness", "Health", "Reflection"]
tags = ["React Native", "Firebase", "Barcode Scanner", "Nutrition", "Project Reflection"]
+++

*By Eric Spencer & Matthew Caballero*  
*December 14, 2024*

---

## Abstract

**HealthUp!** is an application focused on enhancing users’ understanding of their health. With HealthUp!, users can log the nutritional details of foods and track their workouts. We developed this app to support our passion for healthy living by offering features like barcode scanning for nutrition data and a workout diary—all built as a free alternative to subscription-based solutions.

---

## Table of Contents

1. [Project Participants](#project-participants)
2. [Project Narrative](#project-narrative)
   - [Original Project Idea](#original-project-idea)
   - [Inspiration](#inspiration)
3. [Design & Development](#design--development)
   - [Initial UI Concepts & Navigation](#initial-ui-concepts--navigation)
   - [Design Specifications](#design-specifications)
4. [Testing & Iterative Design](#testing--iterative-design)
5. [Screenshots Throughout Development](#screenshots-throughout-development)
6. [Roadblocks](#roadblocks)
7. [Conclusion](#conclusion)
8. [Repository & Demo Links](#repository--demo-links)
9. [Getting Started](#getting-started)

---

## Project Participants

**Eric Spencer**  
- **Commits:** 82  
- **Code:** 58,800 additions | 38,916 deletions  
- **Key Contributions:**  
  - *NutritionScreen.js, Barcode Scanner API usage, User Context, FitnessScreen.js, HomeScreen.js, and more.*  
- **Responsibilities:**  
  - Presentations, npm dependencies, debugging the app compilation, and significant portions of the nutrition and barcode functionality.

**Matthew Caballero**  
- **Commits:** 22  
- **Code:** 2,466 additions | 526 deletions  
- **Key Contributions:**  
  - *CurrentWorkoutScreen.js, UserSettingsScreen.js, WorkoutDiary.js, Firebase integration, UI layout design, and transferring exercises between screens.*  
- **Responsibilities:**  
  - Presentations, enhancing UI layout, and ensuring Firebase integration works as expected.

---

## Project Narrative

Our primary goal was to simplify the experience for people striving to live a healthier lifestyle. We believe that being fit contributes significantly to a long and happy life. HealthUp! supports users in monitoring what they eat via a macronutrient tracker and in tracking their workouts with an integrated diary. All entries automatically update a central journal that reflects all nutritional and exercise data.

### Original Project Idea

The app starts with a user signing in using their email address, which assigns a unique UserID. Every action—whether logging nutrition or tracking workouts—is then correlated to that UserID in Firebase, allowing seamless synchronization across devices. Once signed in, users can choose between Nutrition, Workouts, and Journal screens. Every food or exercise entry updates the journal, providing a continuous health log.

### Inspiration

Inspired by subscription-based tools like MyFitnessPal (especially their barcode feature) and combining ideas around workouts, we created HealthUp! as a free alternative. This allowed us to focus on a user-friendly experience for both nutrition and fitness tracking.

---

## Design & Development

### Initial UI Concepts & Navigation

- **WelcomeScreen.js:**  
  Introduces the app with its title and navigates users to the sign-in screen.

- **SignInScreen.js:**  
  Allows users to sign in or sign up, then navigate to the Home Screen.

- **HomeScreen.js:**  
  Central navigation provides access to the Nutrition, Workouts, Journal, and Profile screens.

- **NutritionScreen.js & Barcode Scanning:**  
  Users can either search for food items manually or scan barcodes to automatically retrieve nutritional information.

- **WorkoutDiary & CurrentWorkoutScreen.js:**  
  Enable users to select exercises from a recommended list or input custom workouts. A timer is available for rest periods, and workouts are tracked as a diary entry.

- **FitnessScreen.js:**  
  Helps users search for exercises based on muscle groups.

- **JournalScreen.js:**  
  Displays a consolidated view of logged nutrition and workouts.

- **UserInfoScreen.js / Profile Screen:**  
  Provides account details like username, email, and weight.

### Design Specifications

The app employs a minimal and consistent color scheme (excluding the more distinctive welcome/login screens) to keep the focus on data entry and tracking. This clean design ensures that users are not distracted and can easily interact with the core features of the app.

---

## Testing & Iterative Design

Our development process was iterative. Early on, we faced challenges with npm dependencies and native builds that took extensive debugging—particularly when integrating barcode scanning features. Key points include:

- The barcode functionality was designed to pass UPC codes to NutritionScreen to retrieve food data automatically.
- Extensive debugging was required to reconcile differences in Android and iOS native configurations.
- **Important:** The iOS version of the app is currently non-functional. There’s a bolded note in the “Testing & Iterative Design” section for anyone attempting to run the app.

---

## Screenshots Throughout Development

Early development was documented with screenshots that tracked progress from initial UI concepts (captured in OneNote) to a more refined Minimum Viable Product. These images show:

- The evolution from a basic layout to more polished screens.
- Various states and error messages during development.
- Improvements in navigation and the integration of the barcode scanning module.

---

## Roadblocks

- **Native Build Errors:**  
  Ongoing challenges with Android/iOS files—especially when integrating packages like `react-native-vision-camera`—resulted in significant debugging efforts.

- **iOS Version Issues:**  
  The current release does not support iOS; only the Android version is stable.

- **Session Persistence:**  
  Users must log in each time as the app lacks a persistent sign-in state. Signing out only occurs through an app restart.

- **Git Management:**  
  Merging divergent branches and handling node module issues led to complications in the commit history.

- **UI/UX Constraints:**  
  Although functionality was prioritized, additional enhancements (e.g., a custom workout list, weight/height logging for better DV% calculations) remain as future improvements.

---

## Conclusion

The HealthUp! project was an enriching journey in mobile development with React Native. Despite challenges, especially in native integration and dependency management, we achieved roughly 95% of our vision. The project taught us valuable lessons in project management, iterative design, and collaborative development, skills that are essential for our future careers.

---

## Repository & Demo Links

- **Repository (without keys):** [HealthUp! Repository](https://github.com/EricSpencer00/HealthUp-)
- **Mid-Project Demo:** [Watch on YouTube](https://youtube.com/shorts/W9zFw_DEovk?si=WDZh0-gq7Xn4-bH2)
- **Final-Project Demo:** [Watch on YouTube](https://youtube.com/shorts/P4aK_aXt1Gk?si=4_iR_fdqSYEZ1HSh)
- **Final Presentation:** C322 Fit Slides

---

## Getting Started

Follow these steps to set up and run HealthUp! locally:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/EricSpencer00/HealthUp-.git
   cd HealthUp-
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # OR
   yarn install
   ```

3. **Start the Metro Bundler:**
   ```bash
   npm start
   # OR
   yarn start
   ```

4. **Run the Application:**

   - **For Android:**
     ```bash
     npm run android
     # OR
     yarn android
     ```
   - **For iOS:**  
     **Note:** The iOS version currently does not work.
     ```bash
     cd ios
     pod install
     cd ..
     npm run ios
     # OR
     yarn ios
     ```

---

Each major folder corresponds to a key part of the project—from native code for Android/iOS to the React components and Firebase integration.

---

## Usage & Development

- **Running Tests:**  
  This project uses Jest for testing. To run the tests:
  ```bash
  npm test
  # OR
  yarn test
  ```

- **Building for Production:**  
  Configure signing keys and release settings in the Android and iOS directories based on the React Native documentation.

- **Continuous Integration:**  
  Integrate with CI/CD pipelines using your preferred tools (e.g., GitHub Actions, CircleCI) based on the scripts defined in `package.json`.

---
