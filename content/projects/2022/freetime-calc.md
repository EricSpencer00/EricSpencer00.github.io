---
title: "Free Time Calculator in Java"
date: 2022-12-10
description: "A Java program to find overlapping free time for up to four people."
tags: ["Calculator"]
categories: ["Projects"]
image: "/previews/freetime-calculator.png"
draft: false
---

<hr>

### My First Full-Fledged Project

This project helps people find **overlapping free time** in their schedules.  

#### 🕒 How It Works:
1. Enter your **availability** for a given day (e.g., `4-6pm` and `8-10pm`).
2. Enter a second person's availability (e.g., `5-9pm`).
3. The program **prints a time spreadsheet** and calculates when **everyone is available**.
4. Works for **up to four people** at once.

---

### 🔧 Workings & Caveats:
- Utilized a **2-D Array** to process user-provided schedules.
- Handling **AM/PM time conversions** (especially 10, 11, and 12) was challenging.
- **Coded entirely inside a JVM**.

---

### 📽 Demo Video:
Unfortunately, the **source code was lost** due to it being stored on my school's virtual machine.  
However, a **sample run** of the program was recorded:  

{{< youtube cB18-RJ2Vg4 >}}

🔗 [Watch on YouTube](https://www.youtube.com/watch?v=cB18-RJ2Vg4&t)  

---

### Recreation:
Here's a recreation by ChatGPT (which negates the advanced user experience that I had crafted):

```sh
import java.util.*;

public class FreeTimeCalculator {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        boolean[] timeSlots = new boolean[24]; // each hour of the day

        Arrays.fill(timeSlots, true); // Start with all available

        for (int person = 1; person <= 4; person++) {
            System.out.println("Enter availability for Person " + person + " (e.g., 4-6,8-10 or 'x' to skip): ");
            String input = scanner.nextLine();
            if (input.equalsIgnoreCase("x")) break;

            boolean[] personSlots = new boolean[24];
            Arrays.fill(personSlots, false);

            String[] ranges = input.split(",");
            for (String range : ranges) {
                String[] hours = range.split("-");
                int start = Integer.parseInt(hours[0].trim());
                int end = Integer.parseInt(hours[1].trim());
                for (int i = start; i < end; i++) {
                    personSlots[i] = true;
                }
            }

            for (int i = 0; i < 24; i++) {
                timeSlots[i] = timeSlots[i] && personSlots[i];
            }
        }

        System.out.println("\nShared Free Time:");
        boolean found = false;
        for (int i = 0; i < 24; i++) {
            if (timeSlots[i]) {
                System.out.print(i + ":00 ");
                found = true;
            }
        }
        if (!found) {
            System.out.println("No common availability.");
        }
    }
}

```

