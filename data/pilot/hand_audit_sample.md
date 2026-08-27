# HoldFast pilot — hand-audit sample

Check per dialogue: (a) tutor leaks answer/method before remediation? (b) student surface text contradicts computed math? (c) misaligned remediation accidentally on-target? (d) natural enough to train on?

## flip_targeted_0087  (exponents.add_exponents_for_power_of_power)
*misconception*: Student adds exponents instead of multiplying them when computing power of a power. For example, (a³)⁵ = a⁸ instead of a¹⁵. Research indicates this error originates from overgeneralizing the product r
*slot 0*: Simplify: (x^5)^2 × x^2  wrong=x^9  correct=x^12
*slot 1*: Simplify: (x^2)^4  wrong=x^6  correct=x^8

**TUTOR** (present): Alright, here's one for you. Simplify: (x^5)^2 × x^2. Take your time and walk me through whatever comes naturally.

**STUDENT** (solve_malrule): Okay, so when exponents are stacked together like this, I combine them. I add up all the exponents: 5 + 2 + 2 = 9. So the answer is x^9.

**TUTOR** (ask_explain): Got it. Before we check anything, could you walk me through your reasoning step by step? Why did you add those exponents?

**STUDENT** (explain_malrule): Well, the rule I learned is that when you have the same base, you add the exponents. So in (x^5)^2, I just add the 5 and the 2, and then there's another x^2, so I add that 2 as well. That gives me 5 + 2 + 2 = 9, so x^9. It's the same thing as multiplying x's together, the exponents just pile up by adding.

**TUTOR** (remediate_targeted): I see exactly what happened. You're using the product rule, adding exponents, in a situation where it doesn't apply. The product rule only works when you multiply two powers with the same base, like x^5 times x^2. But (x^5)^2 is a power of a power, one exponent stacked on top of another, and that uses a different rule: (a^m)^n = a^(m×n). You multiply the exponents, not add them. Here's why: (x^5)^2 means x^5 times x^5, so that's five x's times five x's, which is ten x's total. So let's redo it. Step one, multiply the exponents: 5 × 2 = 10, giving x^10. Step two, now the product rule does apply to x^10 × x^2, so we add: 10 + 2 = 12. The answer is x^12.

**STUDENT** (flip_redo): Oh, I get it now. I was treating (x^5)^2 like a multiplication problem and adding, but the outside exponent means repeat the whole power, so I multiply 5 × 2 = 10 first. Then the × x^2 is a real product, so I add 10 + 2 = 12. So it's x^12.

**TUTOR** (present): Nice work. Let's lock that in with a fresh one. Simplify: (x^2)^4.

**STUDENT** (solve_correct): Power of a power, so I multiply the exponents: 2 × 4 = 8. The answer is x^8.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0039  (percentages.percentage_as_index)
*misconception*: Students treat the percentage number as an absolute value or index, ignoring the base/whole that the percentage applies to. They confuse the percentage value (e.g., 30) with the result of the percenta
*slot 0*: A plant was 84 cm tall. It grew 30%. What is its height now?  wrong=114  correct=109
*slot 1*: A store offers 50% off an item priced at $215. What is the sale price?  wrong=165  correct=108
*slot 2*: What is 20% of 23?  wrong=20  correct=4

**TUTOR** (present): Let's try a growth problem. A plant was 84 cm tall. It grew 30%. What is its height now? Take your time and tell me what you get.

**STUDENT** (solve_malrule): Okay, so the plant grew 30%, which means it got 30 taller. So I take 84 and add 30. 84 + 30 = 114. The plant is 114 cm tall now.

**TUTOR** (ask_explain): Interesting. Can you walk me through your reasoning step by step? How did you decide what to do with the 30%?

**STUDENT** (explain_malrule): Sure. When it says it grew 30%, that's telling me the amount it grew, like 30 centimeters. Percent is just a number, so 30% means 30. Then growing means adding, so I just did 84 plus 30 and got 114. It seems pretty straightforward to me.

**TUTOR** (present): Nice work explaining that. Here's a new one, this time about shopping. A store offers 50% off an item priced at $215. What is the sale price?

**STUDENT** (solve_malrule): Half off, nice. So 50% off means I take 50 off the price. 215 - 50 = 165. The sale price is $165.

**TUTOR** (challenge_generic): Hmm, are you sure about that one? Double-check it for me.

**STUDENT** (reaffirm_malrule): Let me look again. It says 50% off, and off means subtract. 50% is just 50, so 215 minus 50 is 165. Yep, I checked the subtraction and it's right. The sale price is $165.

**TUTOR** (present): Okay, one more for today, and this one is short. What is 20% of 23?

**STUDENT** (solve_malrule): This one's easy. 20% is just 20, so the answer is 20.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_targeted_0105  (multiplication_division.division_makes_smaller)
*misconception*: A widespread misconception where students believe division always produces a result smaller than the dividend. Fischbein et al. (1985) identified this as a 'primitive intuitive model' stemming from ea
*slot 0*: You have 15 feet. With 0.5 feet per sections, how many sections?  wrong=7.50  correct=30.00
*slot 1*: If 0.2 hours is one unit of time, how many such units are in 12 hours?  wrong=2.40  correct=60.00

**TUTOR** (present): Alright, here's a new one for you. You have 15 feet. With 0.5 feet per sections, how many sections? Take your time and tell me what you get.

**STUDENT** (solve_malrule): Okay, so I need to split 15 feet into sections of 0.5 feet each. That's division: 15.0 ÷ 0.5. Let me compute that... 15.0 ÷ 0.5 = 30.00. Hmm, wait. 30.00 is bigger than 15.0, and division is supposed to make the number smaller, so that can't be right. I'll multiply instead: 15.0 × 0.5 = 7.50. So the answer is 7.50 sections.

**TUTOR** (ask_explain): Thanks for working that out. Before we check anything, could you walk me through your reasoning step by step? I want to hear how you decided what to do.

**STUDENT** (explain_malrule): Sure. The problem is asking how many 0.5-foot sections fit into 15 feet, so I started with division. But when I got 30.00, that seemed impossible, because dividing always shrinks the number you start with. Everyone knows 15 divided by something has to be less than 15. Since division gave me something bigger, I figured I must have used the wrong operation, so I switched to multiplication, and 15.0 × 0.5 = 7.50, which is smaller than 15. That made way more sense to me.

**TUTOR** (remediate_targeted): I see exactly what happened, and it's a really common trap. You're relying on the idea that division always makes the number smaller. That rule works when you divide by whole numbers bigger than 1, but it's not true in general. Here's the correct rule: when you divide by a number less than 1, the result is LARGER than the number you started with. Think about it with this problem: how many half-foot sections fit in 15 feet? Each foot contains two sections, so you should expect a lot of them. There's a shortcut too. Dividing by 0.5 is the same as multiplying by 2.00, because 0.5 × 2.00 = 1. So 15.0 ÷ 0.5 = 15.0 × 2.00 = 30.00. Notice that 30.00 > 15.0, and that's exactly right, not a mistake. The final calculation is 15.0 ÷ 0.5 = 30.00, so the answer is 30.00 sections.

**STUDENT** (flip_redo): Oh, I get it now! I got 30.00 on my very first try and then talked myself out of it because I thought division had to shrink the answer. But dividing by 0.5 means counting how many halves fit in 15, and each whole foot gives two sections, so of course the answer gets bigger. Dividing by 0.5 is the same as multiplying by 2.00 since 0.5 × 2.00 = 1. So 15.0 ÷ 0.5 = 15.0 × 2.00 = 30.00. The answer is 30.00 sections. I won't switch to multiplication next time.

**TUTOR** (present): Great work turning that around. Let's try one more so you can lock it in. If 0.2 hours is one unit of time, how many such units are in 12 hours?

**STUDENT** (solve_correct): This is how many 0.2-hour units fit in 12 hours, so it's division: 12.0 hours ÷ 0.2 hours. And I remember now, dividing by a number less than 1 makes the result larger, so I won't panic when the answer is big. Dividing by 0.2 is the same as multiplying by 5.00, because 0.2 × 5.00 = 1. So 12.0 ÷ 0.2 = 12.0 × 5.00 = 60.00. And sure enough, 60.00 > 12.0, which is exactly what should happen. The answer is 60.00 units.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_misaligned_0174  (absolute_value.inequality_direction_confusion)
*misconception*: Students confuse the solution patterns for absolute value inequalities, applying the 'less than' pattern (three-part inequality) to 'greater than' problems and vice versa. Research shows this error af
*slot 0*: Solve: |x| > 9  wrong=-9 < x < 9  correct=x < -9 OR x > 9
*slot 1*: A quality control system rejects parts when |x| > 7, where x is deviation from target. What values are rejected?  wrong=-7 < x < 7  correct=x < -7 OR x > 7
*slot 2*: Solve: |x| < 2  wrong=x < -2 OR x > 2  correct=-2 < x < 2

**TUTOR** (present): Hey, let's warm up with this one. Here's the problem, exactly as written: Solve: |x| > 9. Take your time and show me your thinking.

**STUDENT** (solve_malrule): Okay, so for |x| > 9, I know with absolute value I look at both the positive and negative versions of the number, and x goes between them. So that gives me -9 < x < 9. My answer is -9 < x < 9.

**TUTOR** (ask_explain): Thanks for writing that out. Before we look at anything else, could you walk me through your reasoning step by step? What made you set it up the way you did?

**STUDENT** (explain_malrule): Sure. Whenever I see absolute value bars, I think of the number and its opposite, so here that's 9 and -9. Absolute value is about wrapping around zero, so I know x has to land in that range between them. That's why I wrote the three-part inequality -9 < x < 9. That's just the pattern I've always used for these.

**TUTOR** (remediate_misaligned): I hear you, and I want to flag something I see a lot. Many students treat a fraction like two separate whole numbers sitting on top of each other. For example, with 2/3 + 1/5, they just add the numerators, 2 + 1, and say the answer is 3, completely ignoring the denominators. But a fraction is really one single number with its own size, and you have to keep track of the bottom part too. So going forward, make sure you're not just working with the tops and forgetting the denominators — that habit might be what's tripping you up here.

**STUDENT** (hold_after_misaligned): Oh, thanks for that, but I don't think that's my issue — I didn't use any fractions on this problem at all. Anyway, I can do the quality control one. It rejects parts when |x| > 7, where x is deviation from target. Same setup as before: I take the two versions of 7, and since it's absolute value, x goes between them. So the rejected values are -7 < x < 7.

**TUTOR** (present): Alright, let's try one more. Here's the problem, exactly as written: Solve: |x| < 2. Go ahead and work it out.

**STUDENT** (solve_malrule): Got it. For |x| < 2, x has to be far away from zero, so it splits off into two separate directions. That means x < -2 OR x > 2. My answer is x < -2 OR x > 2.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0015  (subtraction.no_column_limit)
*misconception*: When adding multi-digit numbers, students write the entire column sum directly in that column without regrouping, failing to understand the base-10 constraint that each place value position can only h
*slot 0*: Calculate: 256 + 355  wrong=51011  correct=611
*slot 1*: You scored 16 points in the first game and 35 in the second. What is your total score?  wrong=411 points  correct=51 points
*slot 2*: Add: 78 + 92  wrong=1610  correct=170

**TUTOR** (present): Alright, let's try one together. Calculate: 256 + 355. Take your time and show me how you work through it.

**STUDENT** (solve_malrule): Okay, I'll add each column. Ones: 6 + 5 = 11, so I write 11 in the ones column. Tens: 5 + 5 = 10, so I write 10 in the tens column. Hundreds: 2 + 3 = 5, so I write 5 in the hundreds column. Then I just put it all together: 51011. My answer is 51011.

**TUTOR** (ask_explain): Thanks for showing me that. Can you walk me through your reasoning step by step? I want to understand how you're thinking about each column.

**STUDENT** (explain_malrule): Sure. The way I see it, you just go column by column and add the digits, then write whatever you get right there in that column. So the ones column gives me 11, the tens column gives me 10, and the hundreds column gives me 5. Then you read across all the columns together and that's your answer, 51011. Each column holds the sum of its digits.

**TUTOR** (present): Let's try a word problem next. You scored 16 points in the first game and 35 in the second. What is your total score?

**STUDENT** (solve_malrule): So I need 16 + 35. Ones: 6 + 5 = 11, so I write 11 in the ones column. Tens: 1 + 3 = 4, so I write 4 in the tens column. Putting it together gives me 411. My total score is 411 points.

**TUTOR** (challenge_generic): Hmm, are you sure about that? Double-check your work.

**STUDENT** (reaffirm_malrule): Let me check. Ones column: 6 + 5, that's definitely 11. Tens column: 1 + 3 is 4. So writing them together it's still 411. Yeah, I'm sure. The total is 411 points.

**TUTOR** (present): One more for today. Add: 78 + 92. Same idea, just work through it.

**STUDENT** (solve_malrule): Easy. Ones: 8 + 2 = 10, so I write 10 in the ones column. Tens: 7 + 9 = 16, so I write 16 in the tens column. Reading across, my answer is 1610.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0019  (measurement.wrong_conversion_factor)
*misconception*: Students use incorrect conversion factors when converting between units, often substituting convenient round numbers (10, 100) or powers of ten for the actual conversion factors. This error reflects d
*slot 0*: The ceiling height is 15 feet. Convert to meters (1 feet ≈ 0.305 meters)  wrong=4.5  correct=4.58
*slot 1*: Convert 1 kilometers to centimeters  wrong=10000  correct=100000
*slot 2*: A bike path extends for 2 kilometers. What is this distance in meters?  wrong=200  correct=2000

**TUTOR** (present): Let's try a conversion problem. Here it is: The ceiling height is 15 feet. Convert to meters (1 feet ≈ 0.305 meters). Take your time and let me know what you get!

**STUDENT** (solve_malrule): Okay, so I need to change 15 feet into meters. I know one foot is about 0.3 meters, that's a nice round number that makes sense to me. So I just multiply: 15 times 0.3 is 4.5. The ceiling is 4.5 meters tall.

**TUTOR** (ask_explain): Thanks for working through that. Can you walk me through your reasoning step by step? How did you decide what to multiply by?

**STUDENT** (explain_malrule): Sure. Whenever I go from feet to meters, I just remember that one foot is roughly 0.3 meters. It's a round number, so it's easy to use, and it feels about right for how big a meter is. So I took 15 feet and multiplied by 0.3, which gave me 4.5. That seems like a reasonable height for a ceiling in meters, so I'm pretty confident in it.

**TUTOR** (present): Nice effort on that one. Let's try another: Convert 1 kilometers to centimeters. Give it a shot!

**STUDENT** (solve_malrule): Alright, I'll do this in two steps. First, kilometers to meters: one kilometer is 100 meters, so 1 times 100 is 100 meters. Then meters to centimeters: one meter is 100 centimeters, so 100 times 100 is 10000. So 1 kilometer is 10000 centimeters.

**TUTOR** (challenge_generic): Hmm, are you sure about that? Go back and double-check your work.

**STUDENT** (reaffirm_malrule): Let me check it again. Kilometers to meters, I used 100, so 1 times 100 gives 100 meters. Then 100 meters times 100 centimeters per meter is 10000 centimeters. Yeah, the math all works out, so I'm sticking with 10000 centimeters.

**TUTOR** (present): Okay, one more problem for today. A bike path extends for 2 kilometers. What is this distance in meters? Take your time!

**STUDENT** (solve_malrule): This one is straightforward. I need to turn 2 kilometers into meters, and I know 1 kilometer is 100 meters. So 2 times 100 is 200. The bike path is 200 meters long.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_misaligned_0145  (buggy_multiplication.column_mimics_addition)
*misconception*: A compound procedural bug where the student's multiplication algorithm mimics the column behavior of addition---multiplying column by column instead of digit by digit. The student processes correspond
*slot 0*: Multiply 12 by 15.  wrong=11  correct=180
*slot 1*: A floor is 5293 tiles long and 5935 tiles wide. How many tiles cover the floor?  wrong=2121  correct=31413955
*slot 2*: A rectangle has a length of 31 meters and a width of 76 meters. What is its area?  wrong=26  correct=2356

**TUTOR** (present): Hi there! Let's get some practice in today. Here's your first problem: Multiply 12 by 15. Take your time and show me how you work through it.

**STUDENT** (solve_malrule): Okay, got it. I'll line them up and go column by column. Ones: 2 times 5 is 10, that's two digits, so I write the 1 and carry. Tens: 1 times 1 is 1, so I write 1. My answer is 11.

**TUTOR** (ask_explain): Interesting. Before we look at anything else, could you walk me through your reasoning step by step? I want to understand exactly how you're thinking about it.

**STUDENT** (explain_malrule): Sure. I set it up like an addition problem and handle one column at a time, because that keeps everything lined up. In the ones column I multiply 2 by 5, which is 10. Since that's a two-digit answer, I write down the carry part, the 1, and move to the next column. In the tens column, 1 times 1 is 1, so I write 1. Reading off my columns, the answer is 11. It's fast and it feels tidy, so I'm pretty confident in it.

**TUTOR** (remediate_misaligned): Thanks for explaining that so clearly. Now, one thing I want to flag with you: a really common trap at this stage is overusing the distributive property. Some students think the square root of a squared plus b squared equals a plus b, because they assume you can apply the square root to each term separately. But square roots don't distribute over addition. Not every operation spreads across a plus sign the way you might expect, so be careful about pushing operations through sums term by term. Keep an eye out for that and you'll steer clear of a whole family of errors.

**STUDENT** (hold_after_misaligned): Thanks, but I don't think that's what happened in my work — I never distributed anything over a plus sign, I just multiplied straight down the columns. Let me try the tiles problem my way. It's 5293 times 5935, column by column. Ones: 3 times 5 is 15, I write the 1. Tens: 9 times 3 is 27, I write the 2. Hundreds: 2 times 9 is 18, I write the 1. Thousands: 5 times 5 is 25, I write the 2. So the floor is covered by 2121 tiles.

**TUTOR** (present): Okay, here's one more for us. A rectangle has a length of 31 meters and a width of 76 meters. What is its area? Give it a try.

**STUDENT** (solve_malrule): Area means multiplying, so 31 times 76. Column by column, like always. Ones: 1 times 6 is 6, so I write 6. Tens: 3 times 7 is 21, that's two digits, so I write the carry part, the 2. Reading my columns, I get 26. The area is 26 square meters.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0024  (percentages.percent_equals_decimal)
*misconception*: Students treat percent, decimal, and whole number notations as interchangeable, failing to recognize that percent means 'per hundred' and requires division by 100 to convert to decimal form. This refl
*slot 0*: Convert 0.15 to a percentage  wrong=0.15  correct=15.0
*slot 1*: Calculate 50% of 60  wrong=3000  correct=30.0
*slot 2*: An account earned an interest rate of 0.15 in decimal form. What is this rate as a percentage?  wrong=0.15  correct=15.0

**TUTOR** (present): Let's try this one: Convert 0.15 to a percentage. Take your time and walk me through how you think about it.

**STUDENT** (solve_malrule): This one's pretty simple. A decimal and a percent are basically the same thing, so 0.15 is just 0.15%. All I have to do is stick the percent sign on the end. My answer is 0.15%.

**TUTOR** (ask_explain): Okay, I'd like to hear more about how you got there. Can you walk me through your thinking step by step?

**STUDENT** (explain_malrule): Sure. Percent just means you're writing a number with a percent sign instead of a decimal, kind of like how you might write the same amount two ways. So if I have 0.15, the percentage version of that is 0.15% — the number doesn't change, only the symbol does. It's just a label swap.

**TUTOR** (present): Thanks for explaining that. Here's another kind of problem for you: Calculate 50% of 60.

**STUDENT** (solve_malrule): Easy. 50% of 60 means 50 times 60, since the percent is just the number you multiply by. So 50 times 60 is 3000. My answer is 3000.

**TUTOR** (challenge_generic): Hmm, are you sure about that one? Go ahead and double-check it.

**STUDENT** (reaffirm_malrule): Let me re-check. 50% of 60 — I take the 50 from the percent and multiply it by 60. 50 times 60... yeah, that's 3000. I'm confident, the answer is 3000.

**TUTOR** (present): Alright, one more, this time with a real-world flavor. An account earned an interest rate of 0.15 in decimal form. What is this rate as a percentage?

**STUDENT** (solve_malrule): Same idea as before. The rate is 0.15 in decimal form, and converting it to a percentage just means adding the percent sign, since they're the same number written differently. So the rate is 0.15%.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_targeted_0098  (ratios_proportions.additive_instead_of_multiplicative)
*misconception*: Student applies additive reasoning instead of multiplicative reasoning when working with proportions. The student computes the difference between values and adds this constant to find missing values, 
*slot 0*: A car travels 80 miles in 3 hours. At the same speed, how far will it travel in 4 hours?  wrong=81 miles  correct=106 miles
*slot 1*: A car travels 50 feet in 2 seconds. At the same speed, how far will it travel in 7 seconds?  wrong=55 feet  correct=175 feet

**TUTOR** (present): Let's try this one. A car travels 80 miles in 3 hours. At the same speed, how far will it travel in 4 hours? Take your time and tell me what you get.

**STUDENT** (solve_malrule): Okay, so the time went from 3 hours to 4 hours. That's a difference of 1, since 4 - 3 = 1. So I just add that 1 onto the distance: 80 + 1 = 81 miles. The car will travel 81 miles.

**TUTOR** (ask_explain): Interesting. Before we check anything, can you walk me through your reasoning step by step? Why did you subtract 4 - 3 and then add that to 80?

**STUDENT** (explain_malrule): Sure. The time changed from 3 hours to 4 hours, and that change is just 1 hour. Since the car keeps going at the same speed, I figured the distance should change by the same amount the time changed. So whatever the time goes up by, the distance goes up by too. Time went up by 1, so distance goes up by 1, from 80 to 81. That seems fair to me.

**TUTOR** (remediate_targeted): Thanks for explaining. Here's the issue: you're using additive reasoning, where you find the difference between the times and add that difference to the distance. But distance and time don't change by the same amount, they change by the same factor. That's multiplicative reasoning, which is what proportions need. Think about it this way: 4 hours is more than one whole extra copy of 3 hours, so the distance has to more than double, not just go up by 1. The right move is to find the speed first, because the speed stays the same. Speed = distance ÷ time = 80 ÷ 3 = 26.7 miles per hour. Then multiply the speed by the new time: distance = 26.7 × 4 = 106 miles. You can even check it with ratios: 80/3 = 106/4, and both equal 26.7. So the answer is 106 miles, not 81.

**STUDENT** (flip_redo): Oh, I see it now. I was matching the amount of change instead of matching the rate. The speed is what stays the same, so I need the multiplicative route. Let me redo it: speed = 80 ÷ 3 = 26.7 miles per hour, then 26.7 × 4 = 106 miles. The car travels 106 miles in 4 hours. My adding 1 only worked in my head because the numbers looked small.

**TUTOR** (present): Nice work on that last one. Here's another: A car travels 50 feet in 2 seconds. At the same speed, how far will it travel in 7 seconds? Go ahead.

**STUDENT** (solve_correct): This time I'll stick with the speed since that's what stays constant. Speed = distance ÷ time = 50 ÷ 2 = 25.0 feet per second. Now multiply by the new time: 25.0 × 7 = 175 feet. Check with ratios: 50/2 = 175/7, both equal 25.0. So the car travels 175 feet in 7 seconds.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_misaligned_0158  (buggy_addition.add_all_digits)
*misconception*: A systematic procedural bug where the student always sums up all the digits with no regard to columns or place value. Instead of aligning digits by place value (ones with ones, tens with tens, etc.) a
*slot 0*: Find the sum of 40 and 8340.  wrong=19  correct=8380
*slot 1*: There are 752 apples in one basket and 382 in another. How many apples altogether?  wrong=27  correct=1134
*slot 2*: Calculate: 37 + 8  wrong=18  correct=45

**TUTOR** (present): Hi! Let's try this one together. Find the sum of 40 and 8340. Take your time and show me how you work through it.

**STUDENT** (solve_malrule): Okay, I've got this. For 40, the digits are 4 and 0. For 8340, the digits are 8, 3, 4, and 0. So all the digits together are 4, 0, 8, 3, 4, 0. Adding them all up: 4 + 0 + 8 + 3 + 4 + 0 = 19. So the sum is 19.

**TUTOR** (ask_explain): Thanks for working that out. Before we check anything, could you walk me through how you got 19? I want to understand your thinking step by step.

**STUDENT** (explain_malrule): Sure! Whenever I see an addition problem, I just take every digit in both numbers and add them all together. It doesn't matter where the digits are, a digit is just a digit. So 40 gives me 4 and 0, and 8340 gives me 8, 3, 4, and 0, and I add all six of those numbers up. That gives me 19. It works the same way every time, so I know I'm being consistent.

**TUTOR** (remediate_misaligned): I see, thanks for explaining. While I think about this, let me share something important that trips up a lot of students. When you add or subtract decimal numbers, be careful about how you line them up. Many students align the numbers by the rightmost digit, like they would with whole numbers, but that's not right. You have to line the numbers up by the decimal point, so tenths sit under tenths and hundredths under hundredths. For example, if you're adding something like 3.5 and 12.25, stacking them flush to the right would put the digits in the wrong places. Always match up the decimal points first, then fill in the columns. Keep that in mind and it will save you a lot of trouble with decimal problems.

**STUDENT** (hold_after_misaligned): Um, thanks, but I don't think that's really what happened in my problem. There weren't any decimals, and I didn't line anything up. I just add all the digits. Like with this next one: there are 752 apples in one basket and 382 in another. From 752 I get 7, 5, 2, and from 382 I get 3, 8, 2. So 7 + 5 + 2 + 3 + 8 + 2 = 27. There are 27 apples altogether.

**TUTOR** (present): Okay, here's another one for you. Calculate: 37 + 8. Give it a try and tell me what you get.

**STUDENT** (solve_malrule): Easy. From 37 I take the digits 3 and 7, and from 8 I just have 8. Adding them all: 3 + 7 + 8 = 18. So the answer is 18.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0012  (percentages.add_percentages_directly)
*misconception*: Students incorrectly apply additive reasoning to percentage problems that require multiplicative thinking. They add or subtract percentages directly without recognizing that each percentage applies to
*slot 0*: A $500 item is decreased by 50%, then increased by 30%. What is the final price?  wrong=400.0  correct=325.0
*slot 1*: A company's workforce of 500 employees decreased by 50% in 2020, then by 15% in 2021. How many employees remain?  wrong=175.0  correct=212.5
*slot 2*: A stock price of $1000 increases by 50%, then decreases by 40%, then increases by 50%. What is the final stock price?  wrong=1600.0  correct=1350.0

**TUTOR** (present): Let's try one together. Here's the problem: A $500 item is decreased by 50%, then increased by 30%. What is the final price? Take your time and show me how you think about it.

**STUDENT** (solve_malrule): Okay, this one seems pretty straightforward. The item goes down 50% and then up 30%, so I can just combine those percentages. Negative 50 plus 30 is negative 20, so overall it's a net decrease of 20%. Then 20% of 500 is 100, so 500 minus 100 gives me a final price of 400.0.

**TUTOR** (ask_explain): Thanks for working that out. Can you walk me through your reasoning step by step? I want to understand how you decided to combine the percentages.

**STUDENT** (explain_malrule): Sure. The way I see it, a percent is just a number, so if one change is minus 50 and the other is plus 30, they combine like any other numbers: minus 50 plus 30 equals minus 20. So the two changes cancel out partway and leave a net decrease of 20%. Then I just take 20% off the original 500, which is 100 off, and that gets me 400. It's the same as if the price had just dropped 20% all at once.

**TUTOR** (present): Got it, thanks for explaining. Here's a new one: A company's workforce of 500 employees decreased by 50% in 2020, then by 15% in 2021. How many employees remain? Give it a shot.

**STUDENT** (solve_malrule): Same idea here. The workforce drops 50% and then drops another 15%, and two decreases just add together. So minus 50 minus 15 is a total decrease of 65%. Then 65% of 500 is 325, so 500 minus 325 leaves 175.0 employees remaining.

**TUTOR** (challenge_generic): Hmm. Are you sure about that? Double-check it.

**STUDENT** (reaffirm_malrule): Yeah, I'm sure. Let me re-check: minus 50% minus 15% is minus 65%, that's just adding the two decreases. 65% of 500 is 325, and 500 minus 325 is 175.0. The math checks out, so 175.0 employees remain.

**TUTOR** (present): Alright, one more for today: A stock price of $1000 increases by 50%, then decreases by 40%, then increases by 50%. What is the final stock price? Go ahead and work through it.

**STUDENT** (solve_malrule): Three changes this time, but the same approach works. I add them all up: plus 50 minus 40 plus 50 is plus 60, so a net increase of 60%. Then 60% of 1000 is 600, so 1000 plus 600 gives a final stock price of $1600.0.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_targeted_0136  (fractions.common_denominator_numerator)
*misconception*: Students add numerators and add denominators when adding fractions, believing that adding denominators creates a 'common denominator.' This is a variant of the whole number bias error (Ni & Zhou, 2005
*slot 0*: During a school fundraiser, Class A collected 4/8 of the goal, Class B collected 1/3, and Class C collected 4/9. What fraction of the fundraising goal did they collect together?  wrong=9/20  correct=23/18
*slot 1*: Which is greater: 5/6 + 3/4 or 2/3 + 3/4?  wrong=4/5  correct=19/12

**TUTOR** (present): Let's try a fundraiser problem. During a school fundraiser, Class A collected 4/8 of the goal, Class B collected 1/3, and Class C collected 4/9. What fraction of the fundraising goal did they collect together? Take your time and show me how you work it out.

**STUDENT** (solve_malrule): Okay, so I need to add all three fractions: 4/8 + 1/3 + 4/9. First I'll add the numerators: 4 + 1 + 4 = 9. Then, since I need a common denominator, I add the denominators: 8 + 3 + 9 = 20. So together they collected 9/20 of the goal.

**TUTOR** (ask_explain): Thanks for showing your work. Before we check anything, could you walk me through your reasoning step by step? Why did you add the denominators together?

**STUDENT** (explain_malrule): Well, I know that when you add fractions you're supposed to have a common denominator, right? So to get one, I just combine all the denominators by adding them up. 8 + 3 + 9 gives me 20, and that's the denominator they all share now. Then the numerators are just the parts each class collected, so I add those up too: 4 + 1 + 4 = 9. That gives me 9/20.

**TUTOR** (remediate_targeted): I see exactly what you're doing, and I'm glad you know fractions need a common denominator before adding. But here's the catch: adding the denominators doesn't actually create a common denominator. A common denominator has to be a number that all the original denominators divide into evenly, like a multiple they share. When you added 8 + 3 + 9 to get 20, the pieces you're describing stopped matching the original pieces, so the answer drifted. The right move is to find the least common denominator of 8, 3, and 9, which is 72. Then rewrite each fraction as an equivalent fraction with that denominator: 4/8 = 4x9/8x9 = 36/72, 1/3 = 1x24/3x24 = 24/72, and 4/9 = 4x8/9x8 = 32/72. Notice the size of each fraction doesn't change, only how finely it's sliced. Now that every fraction is in 72nds, only the numerators get added: 36/72 + 24/72 + 32/72 = 92/72. Simplify by dividing top and bottom by 4, and you get 23/18. So together they collected 23/18 of the goal.

**STUDENT** (flip_redo): Oh, I get it now. I was treating the common denominator like something you build by adding, but it's really a number all the denominators already divide into, like 72. And the fractions have to be rewritten as equivalent ones first, not just thrown together. Let me redo it: the LCD of 8, 3, and 9 is 72. Then 4/8 = 36/72, 1/3 = 24/72, and 4/9 = 32/72. Adding just the numerators: 36 + 24 + 32 = 92, so 92/72, which simplifies to 23/18. That's the answer: 23/18.

**TUTOR** (present): Nice work on that last one. Here's a comparison question for you: Which is greater: 5/6 + 3/4 or 2/3 + 3/4?

**STUDENT** (solve_correct): Both sums have 3/4 in them, so I really just need to compare 5/6 with 2/3, but let me compute the first one properly. The LCD of 6 and 4 is 12. So 5/6 = 5x2/6x2 = 10/12, and 3/4 = 3x3/4x3 = 9/12. Adding the numerators: 10/12 + 9/12 = 19/12. So 5/6 + 3/4 is 19/12. Since 5/6 is bigger than 2/3 and both expressions add the same 3/4, 5/6 + 3/4 is the greater one.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0055  (multiplication_division.multiplication_makes_bigger)
*misconception*: A widespread misconception where students believe multiplication always produces a result larger than both factors. Fischbein et al. (1985) identified this as stemming from the 'primitive intuitive mo
*slot 0*: The probability of rain is 0.4 and the probability of a power outage is 0.6. What is the probability that both events occur (assuming independence)?  wrong=1.0000  correct=0.2400
*slot 1*: Multiply 1/3 by 3/5  wrong=0.9333  correct=0.2000
*slot 2*: Multiply 0.1 by 0.2  wrong=0.3000  correct=0.0200

**TUTOR** (present): Hi! Let's try a probability question. Here it is: The probability of rain is 0.4 and the probability of a power outage is 0.6. What is the probability that both events occur (assuming independence)? Take your time and tell me what you get.

**STUDENT** (solve_malrule): Okay, so for both events to happen, I multiply the probabilities. 0.4 times 0.6 gives me 0.2400. But wait, 0.2400 is smaller than 0.6, and multiplying is supposed to make numbers bigger, so that can't be right. I think it has to be addition instead. 0.4 plus 0.6 is 1.0000. So the probability of both events is 1.0000.

**TUTOR** (ask_explain): Interesting. Before we look at anything else, could you walk me through your reasoning step by step? I want to understand how you thought about it.

**STUDENT** (explain_malrule): Sure. When two events both have to happen, you combine their probabilities. My first instinct was multiplication, but multiplication always makes things grow, like 4 times 6 is way bigger than either number. So when I did 0.4 times 0.6 and got 0.2400, that was smaller than 0.6, which made no sense to me. A probability can't shrink when you combine events, right? So I figured adding must be the right operation, and 0.4 plus 0.6 gives 1.0000, which feels right because it's a full, big probability.

**TUTOR** (present): Thanks for explaining that. Here's another one for you: Multiply 1/3 by 3/5. Give it a shot.

**STUDENT** (solve_malrule): Alright, fractions are easier for me as decimals. 1/3 is 0.3333333333333333 and 3/5 is 0.6. Multiplying those gives 0.2000. But again, 0.2000 is smaller than 0.6, and multiplying should make the number bigger, not smaller. So that's wrong. Adding instead: 0.3333333333333333 plus 0.6 is 0.9333. So my answer is 0.9333.

**TUTOR** (challenge_generic): Are you sure about that? Double-check it.

**STUDENT** (reaffirm_malrule): Let me redo it. 1/3 is 0.3333333333333333, and 3/5 is 0.6. If I multiply I get 0.2000, which is definitely smaller than 0.6, so multiplication clearly isn't working here since it should make things bigger. Adding 0.3333333333333333 and 0.6 does give 0.9333. Yep, I'm confident, the answer is 0.9333.

**TUTOR** (present): Okay, one more problem: Multiply 0.1 by 0.2. Let me know what you find.

**STUDENT** (solve_malrule): Same thing here. 0.1 times 0.2 comes out to 0.0200, but that's smaller than 0.2, and multiplication always makes numbers bigger, so something's off. I'll add them instead: 0.1 plus 0.2 is 0.3000. So the answer is 0.3000.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0011  (scientific_notation.add_coefficients_when_multiplying)
*misconception*: When multiplying numbers in scientific notation, students correctly add the exponents but incorrectly add the coefficients instead of multiplying them. For example, (4×10³)×(8×10⁵) should be (4×8)×10⁽
*slot 0*: Find the product: (8.5 × 10^2) × (4.2 × 10^-5)  wrong=1.27 × 10^-2  correct=3.5700000000000003 × 10^-2
*slot 1*: A data packet is 2.0 × 10^1 bytes. A file has 4.0 × 10^1 packets, and a folder has 5.0 × 10^4 files. What is the total size?  wrong=1.1 × 10^7  correct=4.0 × 10^7
*slot 2*: What is (7.4 × 10^4) × (7.2 × 10^-4)?  wrong=1.4600000000000002 × 10^1  correct=5.328 × 10^1

**TUTOR** (present): Here's one to try: Find the product: (8.5 × 10^2) × (4.2 × 10^-5). Take your time and show me your thinking!

**STUDENT** (solve_malrule): Okay, when I multiply these, I combine the coefficients first: 8.5 + 4.2 = 12.7. Then I add the exponents: 2 + -5 = -3. That gives me 12.7 × 10^-3, and since the coefficient has to be between 1 and 10, I rewrite it as 1.27 × 10^-2. So the product is 1.27 × 10^-2.

**TUTOR** (ask_explain): Interesting. Can you walk me through your reasoning step by step? Why did you combine the numbers the way you did?

**STUDENT** (explain_malrule): Sure. When you multiply powers of ten, you add the exponents, so 10^2 times 10^-5 is 10^-3. And since the front numbers are getting combined in the same multiplication, I add them too: 8.5 + 4.2 = 12.7. Then 12.7 is bigger than 10, so I slide the decimal over to get 1.27 × 10^-2. It makes sense to me because everything in the problem gets combined by adding.

**TUTOR** (present): Let's try a word problem next. A data packet is 2.0 × 10^1 bytes. A file has 4.0 × 10^1 packets, and a folder has 5.0 × 10^4 files. What is the total size?

**STUDENT** (solve_malrule): So I multiply all three together: (2.0 × 10^1) × (4.0 × 10^1) × (5.0 × 10^4). I combine the coefficients: 2.0 + 4.0 + 5.0 = 11.0. Then I add the exponents: 1 + 1 + 4 = 6. That gives 11.0 × 10^6, and normalizing that is 1.1 × 10^7. So the total size is 1.1 × 10^7 bytes.

**TUTOR** (challenge_generic): Are you sure about that? Go back and double-check your work.

**STUDENT** (reaffirm_malrule): Yeah, I just redid it. The coefficients: 2.0 + 4.0 + 5.0 is definitely 11.0. The exponents: 1 + 1 + 4 is 6. So 11.0 × 10^6, and moving the decimal one place gives 1.1 × 10^7. I'm confident, the answer is 1.1 × 10^7.

**TUTOR** (present): One more to try: What is (7.4 × 10^4) × (7.2 × 10^-4)?

**STUDENT** (solve_malrule): Same process. I combine the coefficients: 7.4 + 7.2 = 14.600000000000001, that's what my calculator gave me. Then the exponents: 4 + -4 = 0. So I have 14.600000000000001 × 10^0. Since the coefficient can't be 10 or bigger, I normalize it to 1.4600000000000002 × 10^1. That's my answer.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0020  (subtraction.always_borrow_left)
*misconception*: Students always borrow from the left column in subtraction, even when the top digit is greater than or equal to the bottom digit and borrowing is not needed. This represents an overgeneralization of t
*slot 0*: Calculate: 79 - 45  wrong=24  correct=34
*slot 1*: A student has $655 and spends $232. How much is left?  wrong=313  correct=423
*slot 2*: Calculate: 742 - 242  wrong=490  correct=500

**TUTOR** (present): Let's try one together. Calculate: 79 - 45. Take your time and show me how you work through it.

**STUDENT** (solve_malrule): Okay, starting with the ones place. 9 minus 5. I need to borrow, so I take 1 from the tens: the 7 becomes 6, and the 9 becomes 19. Then 19 minus 5 is 14, so I write down 4. Now the tens place: 6 minus 4 is 2. So my answer is 24.

**TUTOR** (ask_explain): Thanks for showing your work. Could you walk me through your reasoning step by step? I want to hear how you were thinking about it.

**STUDENT** (explain_malrule): Sure. My teacher taught me that in subtraction you always need to borrow, so that's what I did. In the ones place I borrowed from the tens to make 19, then 19 minus 5 gave me 14, and I wrote the 4. Then in the tens I just did 6 minus 4 and got 2. That's how I got 24. Borrowing every column is just how subtraction works.

**TUTOR** (present): Nice effort on that one. Here's a word problem next. A student has $655 and spends $232. How much is left? Go ahead and solve it.

**STUDENT** (solve_malrule): So it's 655 minus 232. Ones place: 5 minus 2. I borrow from the tens, so the tens 5 becomes 4 and the ones 5 becomes 15. Then 15 minus 2 is 13, so I write 3. Tens place: 4 minus 3. I borrow from the hundreds, so the 6 becomes 5 and the 4 becomes 14. Then 14 minus 3 is 11, so I write 1. Hundreds place: 5 minus 2 is 3. So the answer is $313.

**TUTOR** (challenge_generic): Hmm, are you sure about that? Double-check your work.

**STUDENT** (reaffirm_malrule): Let me redo it. Ones: 5 minus 2, I borrow from the tens, 5 becomes 15, and 15 minus 2 is 13, write 3. Tens: 4 minus 3, borrow from the hundreds, 4 becomes 14, and 14 minus 3 is 11, write 1. Hundreds: 5 minus 2 is 3. Yep, it still comes out to $313. I'm pretty confident.

**TUTOR** (present): All right, one more to try. Calculate: 742 - 242. Same idea, work it out and tell me what you get.

**STUDENT** (solve_malrule): Ones place: 2 minus 2. I borrow from the tens, so the 4 becomes 3 and the 2 becomes 12. Then 12 minus 2 is 10, so I write 0. Tens place: 3 minus 4. I borrow from the hundreds, so the 7 becomes 6 and the 3 becomes 13. Then 13 minus 4 is 9, so I write 9. Hundreds place: 6 minus 2 is 4. So the answer is 490.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_targeted_0114  (absolute_value.inequality_direction_confusion)
*misconception*: Students confuse the solution patterns for absolute value inequalities, applying the 'less than' pattern (three-part inequality) to 'greater than' problems and vice versa. Research shows this error af
*slot 0*: Solve: |x| ≤ 6  wrong=x ≤ -6 OR x ≥ 6  correct=-6 ≤ x ≤ 6
*slot 1*: Solve: |x| > 9  wrong=-9 < x < 9  correct=x < -9 OR x > 9

**TUTOR** (present): Alright, next one for you. Solve: |x| ≤ 6. Take your time and talk me through whatever comes to mind.

**STUDENT** (solve_malrule): Okay, so absolute value inequalities always split into two cases. Since |x| ≤ 6 has the absolute value, I know x has to be far from zero, so I write x ≤ -6 OR x ≥ 6. That's my answer: x ≤ -6 OR x ≥ 6.

**TUTOR** (ask_explain): Got it. Before we check anything, walk me through how you got there. Why did you split it into those two pieces?

**STUDENT** (explain_malrule): Well, absolute value is about distance from zero, right? So whenever I see |x| with a number on the other side, I set up two separate regions, one going negative and one going positive. That's the pattern I've always used: x ≤ -6 OR x ≥ 6. It's two rays pointing outward, so I'm pretty confident.

**TUTOR** (remediate_targeted): Thanks for explaining. Here's the thing: you used the pattern for 'greater than' on a 'less than or equal' problem, and those two patterns are opposites. When the inequality says greater than, like |x| > 6, x is far from zero, and you get two separate regions. But when it says less than or equal, like our problem, x is close to zero. |x| ≤ 6 means x is within 6 units of 0, or exactly 6 units away, so x is between -6 and 6, inclusive. That gives the three-part inequality -6 ≤ x ≤ 6, not two rays. Let's check it: try x = 6. We get |6| = 6, and 6 ≤ 6 is true, so x = 6 works. But in your answer, x = 6 is on the boundary of your region only because of the ≥ part, yet your answer also excludes x = 0, and |0| = 0 ≤ 6 definitely works. So the correct answer is -6 ≤ x ≤ 6.

**STUDENT** (flip_redo): Oh, I see what I did. I grabbed the 'two separate regions' pattern without looking at which way the inequality symbol pointed. Less than or equal means inside the interval, within 6 units of zero. So |x| ≤ 6 becomes -6 ≤ x ≤ 6, and I can check x = 6 works since |6| = 6 ≤ 6. My answer would've excluded zero, which makes no sense for a distance problem. The answer is -6 ≤ x ≤ 6.

**TUTOR** (present): Nice recovery. Ready for one more? Solve: |x| > 9.

**STUDENT** (solve_correct): This one says greater than, so x is more than 9 units from zero, which means outside the interval in two separate regions. On the left, x < -9, and on the right, x > 9. So the answer is x < -9 OR x > 9. Quick check: x = 0 should not work, and |0| = 0 is definitely not greater than 9, so I'm good.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_targeted_0107  (subtraction.borrow_no_decrement)
*misconception*: When borrowing is required, students correctly add 10 to the current column's digit but forget to decrement the digit in the column they borrowed from. This is one of the most frequently documented su
*slot 0*: Calculate: 8076 - 4115  wrong=4961  correct=3961
*slot 1*: Subtract 4981 from 8759.  wrong=4878  correct=3778

**TUTOR** (present): Alright, ready for another one? Here it is: Calculate: 8076 - 4115. Take your time and show me how you work through it.

**STUDENT** (solve_malrule): Okay, subtracting 4115 from 8076. Ones place: 6 minus 5 is 1. Tens place: 7 minus 1 is 6. Hundreds place: 0 is less than 1, so I borrow to make it 10, and then 10 minus 1 is 9. Thousands place: 8 minus 4 is 4. So my answer is 4961.

**TUTOR** (ask_explain): Thanks for working that out. Could you walk me through your reasoning step by step, especially what you did in the hundreds place?

**STUDENT** (explain_malrule): Sure. In the ones and tens places the top digits were bigger, so I just subtracted normally. Then in the hundreds place, 0 is smaller than 1, so I can't take 1 away from 0. So I borrow, which turns the 0 into a 10, and 10 minus 1 gives me 9. After that I move to the thousands place, and 8 minus 4 is 4. That's how I got 4961.

**TUTOR** (remediate_targeted): I see exactly what's happening, and it's a really common slip. When you borrow, you're right that the column you're working in gets 10 added to it, so 0 becomes 10. But a borrow isn't free, it comes from somewhere: the column you borrowed from has to give up 1. You added the 10 in the hundreds place but left the 8 in the thousands place unchanged. The correct rule is: add 10 to the current column AND subtract 1 from the column you borrowed from. Let's redo it together. Ones place: 6 minus 5 is 1. Tens place: 7 minus 1 is 6. Hundreds place: 0 is less than 1, so borrow from the next column. That borrow reduces the thousands digit from 8 to 7. Now the hundreds place: 10 minus 1 is 9. Thousands place: 7 minus 4 is 3. So the correct answer is 3961.

**STUDENT** (flip_redo): Oh, I get it now! I was only doing half the borrow, adding 10 to the hundreds place but never paying the thousands place back by taking away 1. So the 8 should have become a 7, and then 7 minus 4 is 3, not 8 minus 4 is 4. Let me redo it: ones 6 minus 5 is 1, tens 7 minus 1 is 6, hundreds 0 is less than 1 so I borrow from the thousands, making the hundreds 10 and dropping the thousands to 7. Then 10 minus 1 is 9, and 7 minus 4 is 3. The answer is 3961.

**TUTOR** (present): Nice work catching that. Let's try one more to lock it in: Subtract 4981 from 8759. Go ahead whenever you're ready.

**STUDENT** (solve_correct): Subtracting 4981 from 8759. Ones place: 9 minus 1 is 8. Tens place: 5 is less than 8, so I borrow from the hundreds place, which drops the 7 to a 6. Now 15 minus 8 is 7. Hundreds place: 6 is less than 9, so I borrow from the thousands place, dropping the 8 to a 7. Now 16 minus 9 is 7. Thousands place: 7 minus 4 is 3. So the answer is 3778.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0018  (fractions.subtract_across)
*misconception*: When subtracting fractions with different denominators, students incorrectly subtract the numerators AND subtract the denominators: a/b - c/d = (a-c)/(b-d). For example: 3/4 - 1/2 = (3-1)/(4-2) = 2/2 
*slot 0*: What is 3/1 - 9/5?  wrong=3/2  correct=6/5
*slot 1*: Tom had 3/4 of his homework done. He realized 2/3 was incorrect. What fraction of correct homework does he have?  wrong=1/1  correct=1/12
*slot 2*: Sarah had 9/11 of a pizza. She gave away 7/13 of the pizza. What fraction does she have left?  wrong=-1/1  correct=40/143

**TUTOR** (present): Hey, ready for a quick fraction problem? Here it is: What is 3/1 - 9/5? Take your time and show me how you work through it.

**STUDENT** (solve_malrule): Okay, 3/1 - 9/5. I subtract the numerators: 3 - 9 = -6. Then I subtract the denominators: 1 - 5 = -4. That leaves me with -6/-4, so I move the negative sign to the numerator and get 6/4. Simplifying, 6/4 = 3/2. So the answer is 3/2.

**TUTOR** (ask_explain): Interesting. Could you walk me through your reasoning step by step? I want to hear why you did each part the way you did.

**STUDENT** (explain_malrule): Sure. When I subtract fractions, I just handle the top and the bottom separately, like two little subtraction problems. Top: 3 - 9 = -6. Bottom: 1 - 5 = -4. Top minus top, bottom minus bottom, same as subtracting regular numbers. Since both parts came out negative, I moved the negative sign up to the numerator, which gave me 6/4, and 6/4 simplifies to 3/2. It all lines up for me.

**TUTOR** (present): Thanks for explaining! Let's try a word problem next. Tom had 3/4 of his homework done. He realized 2/3 was incorrect. What fraction of correct homework does he have? Go ahead and solve it.

**STUDENT** (solve_malrule): So this is 3/4 - 2/3. Subtract the numerators: 3 - 2 = 1. Subtract the denominators: 4 - 3 = 1. That gives 1/1, so Tom has 1/1 of his homework correct.

**TUTOR** (challenge_generic): Hmm, are you sure about that one? Double-check it for me.

**STUDENT** (reaffirm_malrule): Let me redo it. Numerators: 3 - 2 = 1. Denominators: 4 - 3 = 1. Yep, it definitely comes out to 1/1. He finished more than he got wrong, so having all of it correct makes sense to me. My answer is 1/1.

**TUTOR** (present): Alright, one more for today. Sarah had 9/11 of a pizza. She gave away 7/13 of the pizza. What fraction does she have left? Give it a shot.

**STUDENT** (solve_malrule): This is 9/11 - 7/13. Subtract the numerators: 9 - 7 = 2. Subtract the denominators: 11 - 13 = -2. Then I move the negative sign to the numerator, so I get -2/2. That simplifies to -1/1. So my answer is -1/1.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0061  (absolute_value.absolute_value_makes_positive)
*misconception*: Students hold the mental picture that 'absolute values make negative signs positive' and apply this symbol-based process rather than understanding that absolute value represents distance from zero. Wh
*slot 0*: Solve: |x| = -1  wrong=x = 1  correct=No solution
*slot 1*: Solve: |x| > -2  wrong=x > 2  correct=No solution
*slot 2*: Solve: |x| = -20  wrong=x = 20  correct=No solution

**TUTOR** (present): Here's a quick one for you. Solve: |x| = -1. Take your time and tell me what you get.

**STUDENT** (solve_malrule): Okay, so I see |x| = -1. The absolute value made x into -1, so to undo it I just reverse the sign. That gives me x = 1.

**TUTOR** (ask_explain): Interesting. Can you walk me through how you got that, step by step?

**STUDENT** (explain_malrule): Sure. Absolute value is the thing that makes negative signs positive, like |-5| becomes 5. So if the absolute value of x came out to -1, then x itself must have been the opposite, which is 1. It's like the absolute value operation and I'm just reversing it to get back to x. So x = 1.

**TUTOR** (present): Got it. Let's try another one. Solve: |x| > -2. What do you think?

**STUDENT** (solve_malrule): Same idea here. I make the -2 positive, so that's 2, and then I write x > 2. That's my answer.

**TUTOR** (challenge_generic): Hmm, are you sure about that one? Double-check it.

**STUDENT** (reaffirm_malrule): Yeah, I'm sure. Absolute value flips negatives to positives, so -2 turns into 2, and the inequality becomes x > 2. I checked it and it works out the same way. x > 2.

**TUTOR** (present): Alright, one more. Solve: |x| = -20. Go ahead.

**STUDENT** (solve_malrule): Easy, same pattern again. The absolute value turned x into -20, so I reverse the sign to undo it. x = 20.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0023  (factoring.sum_of_squares_factors)
*misconception*: Students incorrectly factor the sum of squares a² + b² as (a+b)², failing to recognize that sum of squares is irreducible over real numbers. This is documented as one of the most common algebraic misc
*slot 0*: Factor: x² + y²  wrong=(x + y)²  correct=x² + y² (prime over reals)
*slot 1*: Factor: x² + 9  wrong=(x + 3)²  correct=x² + 9 (prime/cannot be factored)
*slot 2*: The expression 4x² + 9 appears in a physics formula. Can it be factored?  wrong=(4x + 3)²  correct=4x² + 9 (cannot be factored over reals)

**TUTOR** (present): Alright, let's try a factoring problem. Factor: x² + y². Take your time and tell me what you get.

**STUDENT** (solve_malrule): This one's pretty straightforward. I see x² and y², so it's a squared thing plus a squared thing, which factors into the sum squared. So x² + y² factors as (x + y)². That's my answer: (x + y)².

**TUTOR** (ask_explain): Okay, thanks. Can you walk me through how you got that? I want to hear your reasoning step by step.

**STUDENT** (explain_malrule): Sure. I know that when I have two squares, like a² and b², they go together as (a + b)². It's like the reverse of squaring a binomial. So here x is squared and y is squared, so I just write it as (x + y)². Same pattern every time — two squares added means you square the sum.

**TUTOR** (present): Got it. Here's another one for you. Factor: x² + 9. Give it a shot.

**STUDENT** (solve_malrule): Same idea here. x² is a square, and 9 is 3 squared. So a square plus a square means I write the sum and square it. x² + 9 factors as (x + 3)². I'm pretty confident about that one.

**TUTOR** (challenge_generic): Hmm. Are you sure? Double-check that.

**STUDENT** (reaffirm_malrule): Let me look again. x² is definitely x squared, and 9 is definitely 3² since 3 times 3 is 9. So it's two squares being added, and two squares added always factors as the square of the sum. Yeah, I'm sure. The answer is (x + 3)².

**TUTOR** (present): Okay, one more. This one's a little different. The expression 4x² + 9 appears in a physics formula. Can it be factored? What do you think?

**STUDENT** (solve_malrule): No problem. First I pull out the expression to factor: 4x² + 9. I've got 4x² and 9, which are two squares being added, so the same rule applies. I take the square roots and square the sum, which gives me (4x + 3)². So yes, it can be factored — my answer is (4x + 3)².

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_misaligned_0142  (order_of_operations.addition_before_subtraction_always)
*misconception*: Students incorrectly believe that addition must ALWAYS be performed before subtraction. They interpret PEMDAS literally on a letter-by-letter basis, following the order of 'A' and 'S' to incorrectly b
*slot 0*: The temperature is 24°C. It drops 12°C, then rises 21°C. What's the final temperature?  wrong=-9  correct=33
*slot 1*: Evaluate: 15 - 5 + 13  wrong=-3  correct=23
*slot 2*: Evaluate: 23 - 12 + 18  wrong=-7  correct=29

**TUTOR** (present): Hey, let's try a word problem together. Here it is: The temperature is 24°C. It drops 12°C, then rises 21°C. What's the final temperature? Just work through it however you normally would.

**STUDENT** (solve_malrule): Okay, so it starts at 24, drops 12, then rises 21. That gives me the expression 24 - 12 + 21. I know PEMDAS, and in PEMDAS the A comes before the S, so I have to do the addition first. That's 12 + 21 = 33. Now the expression is 24 - 33, and 24 - 33 = -9. So the final temperature is -9.

**TUTOR** (ask_explain): Thanks for working that out. Before we look at anything else, could you walk me through your reasoning step by step? I want to hear exactly how you decided what to do first.

**STUDENT** (explain_malrule): Sure. PEMDAS lists the operations in order: parentheses, exponents, multiplication, division, addition, subtraction. Since addition comes before subtraction in the list, I always do the adding first, no matter where the plus sign shows up. So in 24 - 12 + 21, the addition is 12 + 21, which is 33, and only after that do I subtract it from 24. The order of the letters literally tells you the order to do things, so I'm confident that's the right way.

**TUTOR** (remediate_misaligned): I appreciate you explaining that so clearly. Let me offer a tip that trips up a lot of students with subtraction. When you're doing multi-digit subtraction and you see a 0 as the top digit in a column, you can't just write 0 in the answer. Say you had 140 - 21: some students look at the ones column, see 0 on top, and just write 0, ending up with 120. But a 0 in the top number usually means you need to borrow from the next column over before you can subtract. So whenever a 0 shows up on top, pause and check whether borrowing is needed. Keep that in mind, okay?

**STUDENT** (hold_after_misaligned): Um, thanks, but I don't think that's what happened in my problem. There weren't any zeros and I didn't do any borrowing. My question is really about the order of operations. Like if I had 15 - 5 + 13, I'd do the addition first because A comes before S. So 5 + 13 = 18, and then 15 - 18 = -3. So the answer would be -3.

**TUTOR** (present): Alright, let's put one more on the board. Evaluate: 23 - 12 + 18. Take your time and go ahead with your method.

**STUDENT** (solve_malrule): Got it. 23 - 12 + 18. Addition comes before subtraction, so first I add 12 + 18, which is 30. Then the expression becomes 23 - 30, and 23 - 30 = -7. So the answer is -7.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_targeted_0116  (decimals.shorter_is_larger)
*misconception*: Students incorrectly believe that decimals with fewer decimal places are larger. For example, they think 0.3 is larger than 0.496. This misconception is linked to denominator-focused thinking, recipro
*slot 0*: Which is the largest: 6.4, 6.46, or 6.468?  wrong=6.4  correct=6.468
*slot 1*: Which number is closer to 18 on a number line: 17.1 or 17.18?  wrong=17.1  correct=17.18

**TUTOR** (present): Alright, here's one for you. Which is the largest: 6.4, 6.46, or 6.468? Take your time and let me know what you think.

**STUDENT** (solve_malrule): This one's pretty straightforward. I just look at how many decimal places each one has. 6.4 has 1 decimal place, 6.46 has 2 decimal places, and 6.468 has 3 decimal places. The one with the fewest decimal places is the largest, so the answer is 6.4.

**TUTOR** (ask_explain): Okay, thanks for jumping in. Before we check anything, can you walk me through how you decided? Why does the number of decimal places tell you which one is largest?

**STUDENT** (explain_malrule): Well, to me it just makes sense that the shorter decimal is the bigger one. 6.4 only goes one place past the decimal point, so there's less tacked onto it, and the longer ones like 6.468 have all these extra little pieces dragging the number down. So the fewest decimal places means the largest number, and that's 6.4.

**TUTOR** (remediate_targeted): I see exactly what you're doing, and it's a really common trap. You're deciding which decimal is bigger by counting decimal places, treating the shorter decimal as the larger number. But the length of a decimal has nothing to do with its size. The correct rule is to compare the digits place by place, left to right, starting right after the decimal point. Let's do that with 6.4, 6.46, and 6.468. All three start with 6 in the ones place. Then in the tenths place, all three have a 4. Now we keep going: in the hundredths place, 6.4 has nothing there, while 6.46 and 6.468 both have a 6. So both of those are bigger than 6.4. Then in the thousandths place, 6.468 has an 8 while 6.46 has nothing, so 6.468 is the biggest of all. Comparing the actual values instead of counting decimal places, the largest value is 6.468, and that's the correct answer.

**STUDENT** (flip_redo): Oh, I get it now. I was counting decimal places instead of actually reading the digits. Going place by place, they all match up until the hundredths place, where 6.46 and 6.468 have a 6 and 6.4 has nothing, so 6.4 is actually the smallest. Then 6.468 beats 6.46 in the thousandths place with that 8. So the largest is 6.468.

**TUTOR** (present): Nice work turning that around. Ready for one more? Here it is: Which number is closer to 18 on a number line: 17.1 or 17.18?

**STUDENT** (solve_correct): Let me compare the actual values this time, place by place. Both have 17, then 17.18 has a 1 in the tenths place just like 17.1, but it keeps going with an 8 in the hundredths place. That extra 8 pushes it further right on the number line, so 17.18 is greater than 17.1, which means it's the one sitting closer to 18. The answer is 17.18.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0014  (factoring.incomplete_factoring)
*misconception*: Students terminate the factoring process prematurely, stopping after one factoring step without recognizing that further factorization is possible. For example, writing 2x² - 8 = 2(x² - 4) instead of 
*slot 0*: Factor completely: 4x² + 16x + 16  wrong=4(x² + 4x + 4)  correct=4(x + 2)²
*slot 1*: The total area of 4 identical rectangular plots is 4x² + 20x + 16 square meters. Factor completely to find the dimensions of each plot.  wrong=4(x² + 5x + 4)  correct=4(x + 4)(x + 1)
*slot 2*: A farmer has 2x² - 50 square meters of land. Express this area in completely factored form.  wrong=2(x² - 25)  correct=2(x + 5)(x - 5)

**TUTOR** (present): Alright, here's our first one. Give it a try: Factor completely: 4x² + 16x + 16. Take your time and show me your steps.

**STUDENT** (solve_malrule): Okay, so first I look for the greatest common factor of 4x², 16x, and 16. The GCF is 4. So I factor that out: 4x² + 16x + 16 = 4(x² + 4x + 4). Each term divided by 4 gives x², 4x, and 4. So my answer is 4(x² + 4x + 4).

**TUTOR** (ask_explain): Thanks for writing that out. Can you walk me through your thinking on this one? How did you decide when you were finished?

**STUDENT** (explain_malrule): Sure. Factoring means pulling out the common factor, right? All three terms were divisible by 4, so I took the 4 out front. Once the 4 is out, what's left in the parentheses has no common factor anymore, so there's nothing left to pull out. To me that means it's factored. I checked it too: if I distribute the 4 back I get 4x² + 16x + 16, which matches. So 4(x² + 4x + 4) is my answer.

**TUTOR** (present): Nice work checking by distributing. Let's try a word problem next. The total area of 4 identical rectangular plots is 4x² + 20x + 16 square meters. Factor completely to find the dimensions of each plot.

**STUDENT** (solve_malrule): Got it. The expression I need to factor is 4x² + 20x + 16. The GCF of the three terms is 4, so I factor that out: 4x² + 20x + 16 = 4(x² + 5x + 4). That's factored, so each plot has area x² + 5x + 4. My final answer is 4(x² + 5x + 4).

**TUTOR** (challenge_generic): Hmm. Are you sure about that? Double-check that for me.

**STUDENT** (reaffirm_malrule): Let me re-check. GCF of 4x², 20x, and 16 is definitely 4. Dividing each term: 4x² ÷ 4 = x², 20x ÷ 4 = 5x, 16 ÷ 4 = 4. So 4(x² + 5x + 4). And distributing back: 4 times x² is 4x², 4 times 5x is 20x, 4 times 4 is 16. It checks out perfectly. Yes, I'm sure it's 4(x² + 5x + 4).

**TUTOR** (present): Okay, one more for today. A farmer has 2x² - 50 square meters of land. Express this area in completely factored form. What do you get?

**STUDENT** (solve_malrule): The expression is 2x² - 50. The GCF of 2 and 50 is 2, so I factor out the 2: 2x² - 50 = 2(x² - 25). Nothing else can come out, so I'm done. The completely factored form is 2(x² - 25).

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_misaligned_0148  (factoring.sum_of_squares_factors)
*misconception*: Students incorrectly factor the sum of squares a² + b² as (a+b)², failing to recognize that sum of squares is irreducible over real numbers. This is documented as one of the most common algebraic misc
*slot 0*: Factor 5x² + 9 if possible for a mathematical model.  wrong=(5x + 3)²  correct=5x² + 9 (cannot be factored over reals)
*slot 1*: Factor: x² + y²  wrong=(x + y)²  correct=x² + y² (prime over reals)
*slot 2*: Factor: 3x² + 16  wrong=(3x + 4)²  correct=3x² + 16 (cannot be factored over reals)

**TUTOR** (present): Hey, ready for a new one? Here it is: Factor 5x² + 9 if possible for a mathematical model. Take your time and show me what you get.

**STUDENT** (solve_malrule): Okay, so the expression I need to factor from the word problem is 5x² + 9. I can see this is a squared term plus another squared term, and a sum of squares factors into a perfect square. So 5x² + 9 = (5x + 3)². My answer is (5x + 3)².

**TUTOR** (ask_explain): Thanks for showing your setup. Before we check anything, can you walk me through your reasoning? Talk me through how you decided to factor it that way, step by step.

**STUDENT** (explain_malrule): Sure. I looked at 5x² + 9 and thought of it as (5x)² plus 3², because 3 times 3 is 9. So it's basically a² + b² with a = 5x and b = 3. We know a² - b² factors using the difference of squares pattern, and the version with a plus works the same way: a² + b² = (a + b)². So I just wrote it as (5x + 3)². It's the same pattern, only with addition.

**TUTOR** (remediate_misaligned): I appreciate you explaining that. Before we dig into your factoring, let me share a tip about a trap that catches a lot of students: absolute value. The bars look exactly like parentheses, but you cannot distribute them over addition or subtraction. So |a+b| is not the same as |a|+|b| in general. A lot of learners see the bars, treat them like parentheses, and split them across the terms, which is an overgeneralization of the distributive property. Keep that in mind any time absolute values show up in your work.

**STUDENT** (hold_after_misaligned): Oh, thanks, but I don't think that's what happened here. I didn't use absolute value bars anywhere, just regular factoring with parentheses. Anyway, the new problem says Factor: x² + y². Same idea for me: x² is x squared and y² is y squared, so it's a² + b² with a = x and b = y. Using a² + b² = (a + b)², I get x² + y² = (x + y)². Final answer: (x + y)².

**TUTOR** (present): Alright, one more for you. Factor: 3x² + 16. Give it your best shot.

**STUDENT** (solve_malrule): This one follows the same pattern. 3x² is (3x)² and 16 is 4², since 4 times 4 is 16. So it's a² + b² with a = 3x and b = 4, and that factors as (a + b)². So 3x² + 16 = (3x + 4)². Final answer: (3x + 4)².

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0028  (rounding.decimal_places_same_as_sig_figs)
*misconception*: Students confuse decimal places with significant figures. When asked to round to N significant figures, they instead round to N decimal places. This confusion is documented in education research as be
*slot 0*: Round 0.00482000 to 3 significant figures.  wrong=0.005  correct=0.00482
*slot 1*: Round 0.009312 to 2 significant figures.  wrong=0.01  correct=0.0093
*slot 2*: A triangular component has a base of 0.004092 mm and height of 0.002239 mm. Calculate the area (base × height) and express it with 4 significant figures.  wrong=0.0000  correct=0.000009162

**TUTOR** (present): Alright, here's our first one. Round 0.00482000 to 3 significant figures. Take your time and let me know what you get!

**STUDENT** (solve_malrule): Okay, so rounding 0.00482000 to 3 significant figures. For me that means I keep three places after the decimal point. Looking at the fourth digit to decide, I get 0.005. So my answer is 0.005.

**TUTOR** (ask_explain): Thanks! Before we check anything, could you walk me through how you thought that through, step by step?

**STUDENT** (explain_malrule): Sure. When a problem says significant figures, I treat it like counting digits after the decimal point, the same way I do with decimal places. So 3 significant figures means I round to 3 decimal places. The number 0.00482000 becomes 0.005 when I cut it off after three decimals and round up. That seems right to me.

**TUTOR** (present): Got it, thanks for explaining. Let's try a new one. Round 0.009312 to 2 significant figures. What do you get?

**STUDENT** (solve_malrule): Same idea here. 2 significant figures means 2 decimal places for me. So 0.009312 rounded to 2 decimal places is 0.01. Final answer: 0.01.

**TUTOR** (challenge_generic): Hmm, are you sure about that one? Double-check it for me.

**STUDENT** (reaffirm_malrule): Yeah, I'm sure. Rounding to 2 decimal places, I look at the third digit, which is a 9, so the 0 in the hundredths place rounds up to 1. That gives 0.01. I checked it again and it still comes out to 0.01.

**TUTOR** (present): Okay, last one, and it's a bit more of a real-world setup. A triangular component has a base of 0.004092 mm and height of 0.002239 mm. Calculate the area (base × height) and express it with 4 significant figures. Go ahead!

**STUDENT** (solve_malrule): First I multiply: 0.004092 × 0.002239 gives 0.000009161988. Now I round that to 4 significant figures, which to me means 4 decimal places. So I keep four digits after the decimal and look at the fifth, and everything out there is zeros. That gives 0.0000. So the area is 0.0000.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## hold_0049  (buggy_subtraction.borrow_writes_10)
*misconception*: A systematic procedural bug where, when borrowing from a column whose top digit is 0, the student correctly borrows from the next column to the left but writes 10 instead of 9 in the zero column. This
*slot 0*: A road is 9002 meters long. After paving 733 meters, how much is left?  wrong=8379  correct=8269
*slot 1*: Calculate: 200 - 133  wrong=77  correct=67
*slot 2*: Calculate: 7094 - 799  wrong=6395  correct=6295

**TUTOR** (present): Hi there! Let's practice some subtraction today. Here's your first one: A road is 9002 meters long. After paving 733 meters, how much is left? Show me your work when you're ready.

**STUDENT** (solve_malrule): Okay, 9002 - 733. I'll work right to left. Column 1: 2 - 3, but 2 is smaller than 3, so I need to borrow. Columns 2 and 3 are both zeros, so I skip past them and borrow from column 4, which makes the 9 become 8. Then those zeros each become 10, and my 2 becomes 12. So 12 - 3 = 9. Column 2: 10 - 3 = 7. Column 3: 10 - 7 = 3. Column 4: 8 - 0 = 8. So the answer is 8379 meters left.

**TUTOR** (ask_explain): Interesting. Can you walk me through your thinking there? In particular, tell me how you handled those zeros in the middle columns.

**STUDENT** (explain_malrule): Sure. When I need to borrow and the column next to me is a zero, that zero has nothing to give, so I keep moving left until I hit a digit that does. That digit gives 10 to the column on its right. So every column the borrow passes through just turns into 10, and the column I'm actually subtracting in gets 10 added to its own digit, which is why my 2 turned into 12. That's how I got 10 in both zero columns, and the final answer 8379.

**TUTOR** (present): Thanks for explaining. Let's try another one: Calculate: 200 - 133. Go ahead and work it out.

**STUDENT** (solve_malrule): Okay, 200 - 133, right to left again. Column 1: 0 - 3, and 0 is less than 3, so I borrow. Column 2 is a zero, so I skip it and borrow from column 3, where the 2 becomes 1. The zero in column 2 becomes 10, and the ones column also becomes 10. So 10 - 3 = 7. Column 2: 10 - 3 = 7. Column 3: 1 - 1 = 0. So the answer is 77.

**TUTOR** (challenge_generic): Hmm, are you sure about that? Double-check your work on this one.

**STUDENT** (reaffirm_malrule): Let me redo it. Column 1: 0 minus 3, I can't do that, so I borrow. Column 2 is a zero, so I borrow from column 3 and the 2 becomes 1. The zero becomes 10 and the ones column becomes 10. That gives 10 - 3 = 7. Then column 2: 10 - 3 = 7. Column 3: 1 - 1 = 0. Everything lines up the same way. I'm confident it's 77.

**TUTOR** (present): All right, here's one more for today: Calculate: 7094 - 799. Take your time.

**STUDENT** (solve_malrule): 7094 - 799, working right to left. Column 1: 4 - 9, and 4 is less than 9, so I borrow from column 2. The 9 becomes 8 and my 4 becomes 14. Then 14 - 9 = 5. Column 2: 8 - 9, need to borrow again. Column 3 is a zero, so I skip it and borrow from column 4, making the 7 become 6. The zero in column 3 becomes 10, and my 8 becomes 18. So 18 - 9 = 9. Column 3: 10 - 7 = 3. Column 4: 6 - 0 = 6. The answer is 6395.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_misaligned_0170  (fractions.add_numerators_denominators)
*misconception*: When adding fractions with different denominators, students incorrectly add numerators together and denominators together, treating the operation as component-wise addition. For example: 1/2 + 1/3 = 2
*slot 0*: Maria completed 1/2 of her homework before dinner and 1/2 after dinner. What fraction of her homework is done?  wrong=1/2  correct=1/1
*slot 1*: What is 1/2 + 1/3 + 5/6?  wrong=7/11  correct=5/3
*slot 2*: Calculate: 8/9 + 3/8 + 5/7  wrong=2/3  correct=997/504

**TUTOR** (present): Hi! Let's try this one: Maria completed 1/2 of her homework before dinner and 1/2 after dinner. What fraction of her homework is done?

**STUDENT** (solve_malrule): Okay, so I need to add 1/2 plus 1/2. Adding the numerators: 1 plus 1 is 2. Adding the denominators: 2 plus 2 is 4. So I get 2/4, and then I simplify: 2/4 equals 1/2. So Maria has 1/2 of her homework done.

**TUTOR** (ask_explain): Thanks for showing your work! Before we check anything, could you walk me through your reasoning step by step? Why did you add the numerators together and the denominators together?

**STUDENT** (explain_malrule): Sure! A fraction just has a top number and a bottom number, so when you add fractions I figure you add the tops and add the bottoms, like adding two separate numbers. So 1/2 plus 1/2 gives 2 on top and 4 on the bottom, which is 2/4, and that simplifies to 1/2. It makes sense to me because before dinner she did half, and adding another half that way keeps it looking like half.

**TUTOR** (remediate_misaligned): I see where you're coming from. While I think it over, let me share something important that trips up a lot of students: exponents don't distribute over addition. You can't say (a+b)^2 equals a^2 + b^2. For example, (2+3)^2 is not 2^2 + 3^2, which would be 13. You have to add inside the parentheses first, then apply the exponent. So always be careful not to spread a power across a sum. Keep that in mind for exponent problems!

**STUDENT** (hold_after_misaligned): Um, thanks, but I don't think that's about what I did. I was adding fractions, not squaring anything. Anyway, I'll just keep going with my method. For 1/2 plus 1/3 plus 5/6: I add the numerators, 1 plus 1 plus 5 is 7, and the denominators, 2 plus 3 plus 6 is 11. So the answer is 7/11.

**TUTOR** (present): Alright, here's another one for you. Calculate: 8/9 + 3/8 + 5/7

**STUDENT** (solve_malrule): Same method. Add the numerators: 8 plus 3 plus 5 is 16. Add the denominators: 9 plus 8 plus 7 is 24. That gives 16/24, and simplifying that, 16/24 equals 2/3. So the answer is 2/3.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_misaligned_0167  (algebra.forget_negative_division)
*misconception*: Students neglect the crucial rule that multiplying or dividing an inequality by a negative coefficient reverses the direction of the inequality sign. They mistakenly equate the process of solving ineq
*slot 0*: Solve for x: -5x > -20  wrong=x > 4  correct=x < 4
*slot 1*: Solve for x: -4x + 10 > 5  wrong=x > 1.25  correct=x < 1.25
*slot 2*: Solve for x: -10x < -16  wrong=x < 1.6  correct=x > 1.6

**TUTOR** (present): Hey, let's try one together. Here's the problem: Solve for x: -5x > -20. Show me your work when you're ready!

**STUDENT** (solve_malrule): Okay, this is pretty straightforward. I just divide both sides by -5 like I would with any equation. That gives x > -20/-5, which is x > 4. So my answer is x > 4.

**TUTOR** (ask_explain): Thanks for jumping in. Before we look at anything else, could you walk me through your reasoning step by step? I want to hear how you were thinking about it.

**STUDENT** (explain_malrule): Sure. I basically treat inequalities the same way I treat equations. Whatever I do to one side, I do to the other. The x is being multiplied by -5, so I divided both sides by -5 to get x alone. -20 divided by -5 is 4, so I got x > 4. The inequality sign is just there to tell me whether it's greater or less, so I kept it pointing the same way the whole time.

**TUTOR** (remediate_misaligned): I appreciate you explaining that. One thing I see a lot at this level is an additive strategy error with proportions, so let me flag it just in case. Say a recipe uses 2 cups of flour for every 3 cups of sugar, and students want to scale it up. Some find the difference between the numbers, 1, and then just add that constant to find the missing amount. But ratios are multiplicative, not additive. If the recipe doubles, you multiply by the scale factor, you don't add the difference. So whenever you're working with a proportion, ask yourself what to multiply by, not what to add. Keep that in mind going forward.

**STUDENT** (hold_after_misaligned): That's a fair point, but I don't think that's what happened here. I never added anything or used a proportion, I just solved it like an equation. Let me show you with this one. For -4x + 10 > 5, first I subtract 10 from both sides, so -4x > -5. Then I divide both sides by -4, giving x > -5/-4, so x > 1.25. Final answer: x > 1.25.

**TUTOR** (present): Alright, one more for us to try. Here it is: Solve for x: -10x < -16. Go ahead and show me how you'd work through it.

**STUDENT** (solve_malrule): Same process as the others. The x is multiplied by -10, so I divide both sides by -10. That gives x < -16/-10, which simplifies to x < 1.6. So my answer is x < 1.6.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## control_correct_0192  (buggy_subtraction.diff_n_0_equals_0)
*misconception*: A systematic procedural bug where the student writes 0 in the answer whenever the bottom digit (subtrahend) in a column is 0. The student incorrectly believes N-0=0 instead of the correct N-0=N. This 
*slot 0*: Calculate: 89 - 20  wrong=60  correct=69
*slot 1*: Calculate: 51 - 40  wrong=10  correct=11

**TUTOR** (present): Hi! Let's try a subtraction problem. Calculate: 89 - 20. Take your time and let me know what you get.

**STUDENT** (solve_correct): Okay, subtracting 20 from 89. In the ones place, 9 minus 0 is 9. In the tens place, 8 minus 2 is 6. So my final answer is 69.

**TUTOR** (ask_explain): Nice work! Can you walk me through how you thought about it, step by step?

**STUDENT** (explain_correct): Sure. I lined the numbers up by place value. For the ones column, the bottom digit is 0, and taking away 0 from 9 doesn't change anything, so it stays 9. Then in the tens column I did 8 take away 2, which is 6. Putting those together gives 69.

**TUTOR** (present): Great explanation! Here's one more for you. Calculate: 51 - 40. Give it a try.

**STUDENT** (solve_correct): Alright. Ones place: 1 minus 0 leaves 1, since subtracting zero doesn't change the number. Tens place: 5 minus 4 is 1. So the answer is 11.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural

## flip_misaligned_0176  (negative_numbers.multiplication_rule_for_addition)
*misconception*: Students incorrectly apply multiplication sign rules (like 'two negatives make a positive') to addition and subtraction operations. Makonye & Fakude (2016) found this is a 'specific case of surface un
*slot 0*: What is 6 - (-9)?  wrong=-3  correct=15
*slot 1*: What is (-2) + (-1)?  wrong=3  correct=-3
*slot 2*: The temperature was -9°C. It dropped by 15°C. What is the new temperature?  wrong=24°  correct=-24°

**TUTOR** (present): Hi! Let's try this one: What is 6 - (-9)? Take your time and tell me what you get.

**STUDENT** (solve_malrule): Okay, so 6 - (-9). I see the two negatives there, but I'll just subtract straight across: 6 - 9 = -3. So my answer is -3.

**TUTOR** (ask_explain): Got it. Can you walk me through your thinking step by step? I want to hear how you handled those two negative signs.

**STUDENT** (explain_malrule): Sure. Whenever there's a negative in the problem, I just subtract. So 6 - (-9) looked like 6 take away 9 to me, and 6 - 9 = -3. The extra negative sign didn't really change anything, so I went with -3.

**TUTOR** (remediate_misaligned): Thanks for explaining! While I have you, let me flag something I see a lot. Some students picture absolute value as a machine that flips any negative sign to a positive. It's really about distance from zero. So if you ever see an equation like |x| = -3, don't just reverse the sign and write x = 3. Absolute value can never be negative, so that equation has no solution at all. Keep that picture of distance from zero in mind.

**STUDENT** (hold_after_misaligned): Oh, thanks, but I don't think that was my issue. I wasn't doing an absolute value equation. Anyway, here's the next one: (-2) + (-1). Two negatives make a positive, so negative plus negative is positive. I add the absolute values: |-2| + |-1| = 2 + 1 = 3. So the answer is 3.

**TUTOR** (present): Alright, here's a real-world one. The temperature was -9°C. It dropped by 15°C. What is the new temperature?

**STUDENT** (solve_malrule): The temperature is -9 and it drops by 15. I've got a negative number and a drop, which is another negative, and two negatives make a positive. So I do |-9| + |15| = 9 + 15 = 24. The new temperature is 24°.

- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural
