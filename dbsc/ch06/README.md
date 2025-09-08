# Chapter 6

## Practice Exercises

### 6.1

Construct an E-R diagram for a car insurance company whose customers own one or more cars each. Each car has associated with it zero to any number of recorded accidents. Each insurance policy covers one or more cars and has one or more premium payments associated with it. Each payment is for a particular period of time, and has an associated due date, and the date when the payment was received.

<details>
<summary>Answer</summary>
<img src="6.1.svg">
</details>

### 6.2 

Consider a database that includes the entity sets student, course, and section from the university schema and that additionally records the marks that students receive in different exams of different sections.

- Construct an E-R diagram that models exams as entities and uses a ternary relationship as part of the design.
- Construct an alternative E-R diagram that uses only a binary relationship between student and section. Make sure that only one relationship exists between a particular student and section pair, yet you can represent the marks that a student gets in different exams.

<details>
<summary>Answer</summary>
<img src="6.2.svg">
</details>

### 6.3

Design an E-R diagram for keeping track of the scoring statistics of your favorite sports team. You should store the matches played, the scores in each match, the players in each match, and individual player scoring statistics for each match. Summary statistics should be modeled as derived attributes with an explanation as to how they are computed.

<details>
<summary>Answer</summary>
<img src="6.3.drawio.svg">

Remarks:
- Having **team** participate in **goal** relationship may seem redundant, but is required to distinguish own goals 

How dervied attributes are computed in entities:
- **fixture**: both `home_score` and `away_score` combine `play` and `goal` relationship sets to count goals scored for respective teams
- **appearance**:
    - `minutes_played` is computed from `minute_entered` and `minute_left`. This simple model does not account for stoppage time in each half.
    - `goals_scored` is based on goal relationship set (own goals excluded)

- **player**: all attributes are aggregated over **played_in** relationship using `goals_scored` and `minutes_played` of each **appearance**
- **team**:
    - `goals_scored` and `goals_conceded` is derived from **goal**
    - To compute `avg_match_goals` the number of games is derived from **play**
</details>
