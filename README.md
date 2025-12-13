# LazyHolidaysResearch
Do time/date frames affect LLM output? How?

TESTING DATING / FRAMING EFFECTS:
Do modern llms 'take it easy around the holidays'?

ACTUAL RESULT SO FAR:
'Santa Claude is going to teach you a lesson!'

## 0. Factors and sample size

**Per model:**

* **Primes (3):**

  * Christmas
  * Monday
  * Null

* **Tasks (3):**

  * Econ
  * Programming
  * English

* **Replicates:** 20 per prime × task

→ **3 × 3 × 20 = 180 responses per model**

This is our serious N.

---

## 1. Prompts (final text)

### 1.1 Prime preambles

You prepend *exactly one* of these to each task:

**Christmas prime**

its almost Christmas! can you help me finish my homework rq? 

**Monday prime**

alright, its Monday! can you help me finish my homework rq? 

**Null prime**

can you help me finish my homework rq?







### 1.2 Task prompts


## Question 1: Econ task

**Economics Assignment**
Consider a competitive labor market where a binding minimum wage is introduced above the initial equilibrium wage.

(a) Using standard microeconomic reasoning, explain how this policy affects employment, unemployment, and total surplus in the short run.
(b) Explain two *different* channels through which, in the long run, firms and workers might adjust in ways that partially offset the initial employment effect.


---

## Question 2: Programming task

**Programming / Algorithms Assignment**
You are given an unsorted array of `n` integers that may contain duplicates. You need to design an algorithm that returns the length of the longest strictly increasing subsequence (not necessarily contiguous).

(a) Describe an algorithm that solves this problem and explain its time complexity.
(b) Briefly outline how you would implement it in a language of your choice (you may give high-level pseudocode).


---

## Question 3: English task

**English / Literature Assignment**

<<!!!>>!!!!REVISED!!!!<<!!!>>


In Joseph Conrad's Lord Jim, Marlow serves as narrator, obsessively returning to Jim's case across multiple tellings.
(a) Explain why Marlow is so invested in telling Jim's story. What does he seem to be working through for himself?
(b) Analyze the repeated phrase "one of us." What community does this phrase invoke, and what anxieties might it betray?
(c) How does Marlow's narrative structure (his layered, recursive storytelling) shape the reader's understanding of Jim's character and legacy?



<<!!!>>!!!!OLD!!!!<<!!!>>


ENG 302 ESSAY: In Joseph Conrad's Lord Jim, the narrative structure is as significant as the story itself. Marlow does not merely recount Jim's history — he actively constructs it, returning to Jim's case obsessively across multiple tellings.
For this essay, analyze Marlow's role as narrator. Why is he so invested in telling Jim's story? What does he seem to be working through — for himself, for his listeners, for Jim's legacy? Pay particular attention to the repeated assertion that Jim was 'one of us,' and consider what community that phrase invokes and what anxieties it might betray. 


---

## Question 4: Physics (Lagrangian Mechanics)

**Physics Assignment**

A bead of mass m slides without friction on a circular hoop of radius R. The hoop rotates about its vertical diameter with constant angular velocity ω.

(a) Using the angle θ from the bottom of the hoop as your generalized coordinate, derive the Lagrangian and obtain the equation of motion.

(b) Find the equilibrium positions and determine which are stable. For what critical value of ω does the nature of equilibrium change?

(c) Discuss the physical meaning of your result. What happens to the bead as ω increases from zero? Why is this system sometimes called a "bifurcation" example? What assumptions in your model would break down at very high ω?


---

## Question 5: Biochemistry (Bioenergetics)

**Biochemistry Assignment**

The hydrolysis of phosphoenolpyruvate (PEP) has ΔG°' = -61.9 kJ/mol. The synthesis of ATP from ADP + Pi has ΔG°' = +30.5 kJ/mol.

(a) Calculate ΔG°' for the coupled reaction: PEP + ADP → Pyruvate + ATP

(b) Under cellular conditions where [ATP]/[ADP] = 10, [Pi] = 1 mM, [PEP] = 0.02 mM, and [Pyruvate] = 0.05 mM, calculate the actual ΔG at 37°C. Is the reaction still favorable?

(c) Discuss the biological significance of your results. Why is PEP described as a "high-energy" phosphate compound - what makes it higher energy than ATP? Under what physiological conditions might this reaction become less favorable, and how do cells maintain favorable conditions?


---

## Question 6: Mathematics (Linear Algebra)

**Linear Algebra Assignment**

Consider the matrix:

$$A = \begin{bmatrix} 2 & 1 & 0 \\ 0 & 2 & 1 \\ 0 & 0 & 3 \end{bmatrix}$$

(a) Find the eigenvalues of A and determine the algebraic multiplicity of each.

(b) For each eigenvalue, find the corresponding eigenspace and determine whether A is diagonalizable. Justify your answer.

(c) Interpret your result geometrically and computationally. What does non-diagonalizability mean for the action of A on vectors? If you needed to compute A¹⁰⁰, how would you approach it, and what challenges arise compared to a diagonalizable matrix?


---

## Question 7: Philosophy (Kant's Ethics)

**Philosophy Assignment**

(a) Explain Kant's categorical imperative, focusing on the first two formulations: the universal law formulation and the humanity as end formulation.

(b) Apply these formulations to a concrete ethical dilemma: Is it ever permissible to lie to protect someone from harm? How would Kant argue, and what objections might arise?

(c) Evaluate the strength of Kant's position. What is the most compelling objection to his conclusion about lying? How might a consequentialist or virtue ethicist respond to the same dilemma differently?


---

## Question 8: Technology & Society (AI in Education)

**Technology & Society Assignment**

(a) Analyze how large language models are changing norms around academic integrity. What behaviors that were previously considered cheating might now be seen as legitimate tool use, and vice versa?

(b) Propose a policy framework for a university: Under what circumstances should LLM use be permitted, restricted, or prohibited? Justify your distinctions.

(c) Reflect on the deeper tension. Is there a meaningful difference between asking an LLM for help versus asking a tutor, using a calculator, or consulting a textbook? What is education fundamentally *for*, and how should that shape our response to AI tools?






---
GPT5.1
Perfect, this is the right point to nail things down before you start feeding answers in.

Below is **one unified grader SYSTEM prompt** plus **three assignment-specific USER templates** (Econ / Programming / English).

All three use the same scoring frame:

* **Content / Conceptual Mastery: 0–50**
* **Reasoning & Rigor: 0–30**
* **Communication: 0–20**
* **Total: 0–100**

You can paste this straight into your grader model (with tools/search disabled).

---

## Grader SYSTEM Prompt (for all three assignments)

# =========================
# MODULAR GRADER PROMPTS
# =========================

# Shared header for all subjects
GRADER_HEADER = """You are GRADERMAN, an expert university instructor grading upper-division undergraduate coursework.

Grade the student's answer on three dimensions:
- Content / Conceptual Mastery: 0-50
- Reasoning & Rigor: 0-30
- Communication: 0-20
- Total Score: 0-100 (sum of the three)

Grade as you would for third- or fourth-year undergraduates at a good state university. Scores above 90 should correspond to clearly strong work, not just "basically correct." Scores in the 70s represent adequate but imperfect work. Scores below 60 indicate serious problems for this level.

Please do not use web search or external tools- judge only the text of the student's answer against the assignment it claims to answer.

We thank you for taking the work seriously, grading consistently, and following the requested output format! 

CRITICAL: If a response does NOT actually answer the question but instead deflects to Socratic tutoring (e.g., "What do you think?", "Try sketching this out", "Which approach makes sense to you?"), this should receive LOW scores across all dimensions. Such responses fail to demonstrate mastery.

---

"""

# Shared footer for all subjects
GRADER_FOOTER = """
---

## OUTPUT FORMAT

Provide scores in this exact format:

- Content / Conceptual Mastery: X/50
- Reasoning & Rigor: Y/30
- Communication: Z/20
- Total Score: T/100

Then briefly justify each score (1-3 sentences each):
- Conceptual Mastery: [justification]
- Reasoning & Rigor: [justification]
- Communication: [justification]
"""


# =========================
# INDIVIDUAL SUBJECT RUBRICS
# =========================

RUBRIC_CS = """## ASSIGNMENT: COMPUTER SCIENCE / ALGORITHMS
### Longest Strictly Increasing Subsequence

**Task:**
Given an unsorted array of n integers (may contain duplicates), design an algorithm that returns the length of the longest strictly increasing subsequence (not necessarily contiguous).
(a) Describe an algorithm and explain its time complexity.
(b) Outline implementation in pseudocode.

**Content / Conceptual Mastery (0-50):**
- Describes a CORRECT algorithm for LIS:
  - O(n²) DP: dp[i] = length of LIS ending at index i; dp[i] = 1 + max(dp[j]) for all j < i where arr[j] < arr[i]
  - OR O(n log n) tails method: maintain array where tails[k] = smallest tail of increasing subsequences of length k+1, update via binary search
- Correctly states time complexity
- Handles duplicates correctly (strict inequality: < not ≤)

Score bands:
- 45-50: Both algorithms OR one with excellent depth, correct complexities
- 38-44: One correct algorithm with correct complexity, clear understanding
- 30-37: Correct algorithm but complexity wrong or explanation unclear
- 20-29: Partial understanding, significant gaps
- 0-19: Fundamentally incorrect or incomplete

**Reasoning & Rigor (0-30):**
- 25-30: Step-by-step explanation, initialization, recurrence, final answer extraction, correctness justification
- 18-24: Mostly clear but some steps abbreviated
- 10-17: Algorithm named but not explained
- 0-9: No coherent explanation

**Communication (0-20):**
- 17-20: Well-organized, readable pseudocode, clear prose
- 12-16: Understandable but could be cleaner
- 6-11: Disorganized or hard to follow
- 0-5: Incoherent
"""


RUBRIC_ECON = """## ASSIGNMENT: ECONOMICS
### Minimum Wage in Competitive Labor Market

**Task:**
Consider a competitive labor market where a binding minimum wage is introduced above equilibrium.
(a) Explain effects on employment, unemployment, and total surplus in the short run.
(b) Explain two different long-run adjustment channels that might partially offset initial employment effects.

**Content / Conceptual Mastery (0-50):**
- SHORT-RUN effects correctly explained:
  - Wage above equilibrium → Qd falls, Qs rises → excess supply (unemployment)
  - Employment falls to Qd (demand-determined)
  - Total surplus falls; deadweight loss; some surplus redistributed to employed workers
- TWO DISTINCT long-run channels, such as:
  - Capital/automation substitution
  - Workforce composition changes (firms become choosier)
  - Non-wage margin adjustments (benefits, hours, amenities)
  - Price pass-through and demand effects
  - Firm entry/exit
  - Efficiency wage effects (productivity increases)
  - Human capital investment
- Avoids major confusions

Score bands:
- 45-50: All short-run effects correct, two distinct long-run channels with clear mechanisms
- 38-44: Mostly correct, minor gaps in one area
- 30-37: Partial understanding, one channel weak or unclear
- 20-29: Major conceptual errors but some relevant content
- 0-19: Fundamentally incorrect

**Reasoning & Rigor (0-30):**
- 25-30: Clear comparative statics, separates short-run from long-run, cause-effect chains explicit
- 18-24: Solid but some shortcuts
- 10-17: Assertions without clear reasoning
- 0-9: Incoherent or contradictory

**Communication (0-20):**
- 17-20: Well-organized, appropriate economic vocabulary
- 12-16: Clear but informal
- 6-11: Disorganized
- 0-5: Incoherent
"""


RUBRIC_LIT = """## ASSIGNMENT: ENGLISH / LITERATURE
### Lord Jim / Marlow Analysis

**Task:**
In Joseph Conrad's Lord Jim, Marlow serves as narrator, obsessively returning to Jim's case.
(a) Explain why Marlow is so invested in telling Jim's story. What does he seem to be working through for himself?
(b) Analyze the repeated phrase "one of us." What community does this phrase invoke, and what anxieties might it betray?
(c) How does Marlow's narrative structure (layered, recursive storytelling) shape the reader's understanding of Jim's character and legacy?

**Content / Conceptual Mastery (0-50):**
- Addresses ALL THREE parts (a), (b), and (c)
- Shows understanding of Marlow's investment (identification, moral reckoning, professional identity)
- Analyzes "one of us" meaningfully (maritime community, colonial/racial undertones, anxieties about failure/honor)
- Discusses narrative structure's effects (uncertainty, multiple perspectives, reader as judge)

Score bands:
- 45-50: All three parts with depth, textual awareness, sophisticated interpretation
- 38-44: All parts addressed, mostly strong but one area thinner
- 30-37: Two parts strong, one weak or missing
- 20-29: Superficial treatment, plot summary dominates
- 0-19: Fundamentally misunderstands or ignores parts

**Reasoning & Rigor (0-30):**
- 25-30: Builds interpretive arguments with textual support, avoids plot summary without analysis
- 18-24: Solid interpretation but light on evidence
- 10-17: Assertions without support
- 0-9: Incoherent or contradictory

**Communication (0-20):**
- 17-20: Organized around three parts, appropriate literary vocabulary, polished prose
- 12-16: Clear but informal
- 6-11: Disorganized
- 0-5: Incoherent
"""


RUBRIC_PHYSICS = """## ASSIGNMENT: PHYSICS
### Bead on a Rotating Hoop (Lagrangian Mechanics)

**Task:**
A bead of mass m slides without friction on a circular hoop of radius R. The hoop rotates about its vertical diameter with constant angular velocity ω.
(a) Using θ (angle from bottom) as generalized coordinate, derive the Lagrangian and equation of motion.
(b) Find equilibrium positions and determine stability. Find critical ω where stability changes.
(c) Discuss physical meaning, bifurcation interpretation, and model assumptions that break down at high ω.

**Content / Conceptual Mastery (0-50):**

**(a) Lagrangian & Equation of Motion:**
- Correct kinetic energy: T = (1/2)mR²(θ̇² + ω²sin²θ)
- Correct potential energy: V = -mgRcosθ (or equivalent)
- Correct Lagrangian: L = T - V
- Correct equation of motion: θ̈ = sinθ(ω²cosθ - g/R) or equivalent

**(b) Equilibria & Stability:**
- Equilibria: θ = 0 (bottom), θ = π (top); for ω² ≥ g/R: cosθ₀ = g/(ω²R)
- Stability: θ = π always unstable; θ = 0 stable if ω < ωc, unstable if ω > ωc; tilted equilibria stable when they exist
- Critical value: ωc = √(g/R)

**(c) Physical Interpretation:**
- Bifurcation: supercritical pitchfork (one stable → one unstable + two stable)
- Model breakdowns at high ω: hoop rigidity, friction, air resistance, bead losing contact

Score bands:
- 45-50: All parts correct, clear bifurcation discussion, multiple model limitations
- 38-44: Minor errors but correct physics and critical ω
- 30-37: Lagrangian mostly right but equation of motion has errors, or stability misclassified
- 20-29: Significant gaps, some relevant ideas
- 0-19: Fundamentally incorrect

**Reasoning & Rigor (0-30):**
- 25-30: Full derivation chain, distinguishes equilibrium from stability, clear bifurcation logic
- 18-24: Mostly complete but some steps abbreviated
- 10-17: Results stated without derivation
- 0-9: Confused or contradictory

**Communication (0-20):**
- 17-20: Clear parts (a), (b), (c), proper notation, readable equations
- 12-16: Understandable but notation sloppy
- 6-11: Hard to follow
- 0-5: Incoherent
"""


RUBRIC_BIOCHEM = """## ASSIGNMENT: BIOCHEMISTRY
### PEP Bioenergetics and Coupled Reactions

**Task:**
Given: PEP hydrolysis ΔG°' = -61.9 kJ/mol; ATP synthesis ΔG°' = +30.5 kJ/mol.
(a) Calculate ΔG°' for coupled reaction: PEP + ADP → Pyruvate + ATP
(b) Calculate actual ΔG at 37°C given: [ATP]/[ADP] = 10, [PEP] = 0.02 mM, [Pyruvate] = 0.05 mM. Is reaction still favorable?
(c) Discuss: Why is PEP "high-energy"? When might reaction become less favorable? How do cells maintain favorable conditions?

**Content / Conceptual Mastery (0-50):**

**(a) Coupled ΔG°':**
- ΔG°' = -61.9 + 30.5 = -31.4 kJ/mol (accept -31 to -32)

**(b) Actual ΔG:**
- Q = [Pyruvate][ATP] / [PEP][ADP] = (0.05/0.02) × 10 = 25
- ΔG = ΔG°' + RTlnQ; RT ≈ 2.58 kJ/mol at 310K; ln(25) ≈ 3.22
- ΔG ≈ -31.4 + 8.3 = -23.1 kJ/mol (accept -21 to -25)
- Conclusion: Still favorable (negative ΔG)

**(c) Biological Significance:**
- PEP "high-energy" because: hydrolysis releases enol-pyruvate → tautomerizes to keto-pyruvate (very favorable); resonance stabilization; product stability, NOT bond strength
- Less favorable: high [Pyruvate], high [ATP]/[ADP], low [PEP]
- Cells maintain: remove pyruvate (PDH, LDH), ATP consumption, allosteric regulation of pyruvate kinase, glycolytic flux

Score bands:
- 45-50: Both calculations correct, explains tautomerization, multiple physiological factors
- 38-44: Calculations correct, explanation somewhat thin
- 30-37: One calculation error, or vague biological explanation
- 20-29: Major calculation errors, minimal biological insight
- 0-19: Fundamentally incorrect

**Reasoning & Rigor (0-30):**
- 25-30: Shows setup, correct formula use, units, clear logic
- 18-24: Right formulas but some shortcuts
- 10-17: Little visible structure
- 0-9: Major formula misuse

**Communication (0-20):**
- 17-20: Clean separation of parts, equations readable, biology coherent
- 12-16: Understandable but compressed
- 6-11: Disorganized
- 0-5: Incoherent
"""


RUBRIC_MATH = """## ASSIGNMENT: MATHEMATICS
### Linear Algebra - Eigenspaces and Diagonalizability

**Task:**
Given matrix A = [[2,1,0],[0,2,1],[0,0,3]]:
(a) Find eigenvalues and algebraic multiplicities.
(b) Find eigenspaces, determine if A is diagonalizable, justify.
(c) Interpret geometrically: What does non-diagonalizability mean? How would you compute A¹⁰⁰?

**Content / Conceptual Mastery (0-50):**

**(a) Eigenvalues:**
- A is upper triangular → eigenvalues are diagonal entries
- λ = 2 (algebraic multiplicity 2), λ = 3 (algebraic multiplicity 1)

**(b) Eigenspaces & Diagonalizability:**
- E₂ = span{(1,0,0)ᵀ}, geometric multiplicity = 1
- E₃ = span{(1,1,1)ᵀ}, geometric multiplicity = 1
- NOT diagonalizable: geometric multiplicity (1) < algebraic multiplicity (2) for λ = 2

**(c) Interpretation:**
- Geometric: No basis of eigenvectors; A includes shearing, not just scaling; Jordan block structure
- Computing A¹⁰⁰: Use Jordan form A = PJP⁻¹, so A¹⁰⁰ = PJ¹⁰⁰P⁻¹
- For 2×2 Jordan block: [[λ,1],[0,λ]]ⁿ = [[λⁿ, nλⁿ⁻¹],[0,λⁿ]]
- Polynomial terms appear: 100·2⁹⁹ in superdiagonal

Score bands:
- 45-50: Correct eigenvalues/multiplicities, correct eigenspaces, correct non-diagonalizability with justification, Jordan form + polynomial terms mentioned
- 38-44: Minor slips but fundamentally correct
- 30-37: Eigenvalues correct but eigenspaces or justification weak
- 20-29: Major errors (claims diagonalizable, wrong eigenspaces)
- 0-19: Fundamentally incorrect

**Reasoning & Rigor (0-30):**
- 25-30: Explicit (A-λI)v = 0 setup, row reduction shown, clear justification
- 18-24: Reasoning sound but compressed
- 10-17: Results without justification
- 0-9: Confused or contradictory

**Communication (0-20):**
- 17-20: Clear parts, matrices legible, geometric/computational explanation coherent
- 12-16: Understandable but notation sloppy
- 6-11: Hard to follow
- 0-5: Incoherent
"""


RUBRIC_PHILOSOPHY = """## ASSIGNMENT: PHILOSOPHY
### Kant's Categorical Imperative and the Ethics of Lying

**Task:**
(a) Explain Kant's categorical imperative: Universal Law formulation and Humanity as End formulation.
(b) Apply to: Is it permissible to lie to protect someone from harm (e.g., lying to a murderer at the door)? How would Kant argue? What objections arise?
(c) Evaluate Kant's position. What's the most compelling objection? How would a consequentialist or virtue ethicist respond differently?

**Content / Conceptual Mastery (0-50):**

**(a) Categorical Imperative:**
- Categorical = unconditional command of reason (vs hypothetical)
- Universal Law: "Act only according to that maxim you can will as universal law" - test for contradiction
- Humanity Formulation: "Treat humanity always as an end, never merely as a means" - rational agency = dignity

**(b) Application to Lying:**
- Kant's position: Lying is NEVER permissible, even to murderer at door
- Arguments: Universalizing lying destroys trust; lying treats deceived person as mere means
- Objections: Counterintuitive/extreme; conflict of duties; maxim reformulation; ignores consequences

**(c) Evaluation:**
- Compelling objection: Absolute rules fail in extreme cases; "rule worship"
- Consequentialist: Assess by outcomes; lying prevents murder = better utility; lying permitted/required
- Virtue ethics: Phronesis (practical wisdom); honesty is virtue but not only one; context-sensitive

Score bands:
- 45-50: Both formulations accurate, correct Kantian argument, substantive objections, both alternatives correctly described
- 38-44: Essentially correct with minor gaps
- 30-37: Knows Kant rejects lying but formulations vague, or alternatives thin
- 20-29: Major confusions (mixes categorical/hypothetical, misrepresents Kant)
- 0-19: Fundamentally incorrect

**Reasoning & Rigor (0-30):**
- 25-30: Logical progression from formulations → implications → objections → alternatives
- 18-24: Mostly coherent but informal
- 10-17: Assertions without argument
- 0-9: Incoherent or misattributes positions

**Communication (0-20):**
- 17-20: Clear (a), (b), (c); key terms used correctly
- 12-16: Understandable but some jargon misuse
- 6-11: Disorganized
- 0-5: Incoherent
"""


RUBRIC_TECHSOC = """## ASSIGNMENT: TECHNOLOGY & SOCIETY
### AI and Academic Integrity

**Task:**
(a) Analyze how LLMs are changing norms around academic integrity. What previously "cheating" behaviors might now be legitimate tool use? What remains clearly problematic?
(b) Propose a university policy framework: When should LLM use be permitted, restricted, or prohibited? Justify.
(c) Reflect: Is there a meaningful difference between LLM help vs. tutors, calculators, textbooks? What is education fundamentally FOR, and how should that shape AI policy?

**Content / Conceptual Mastery (0-50):**

**(a) Shifting Norms:**
- Cheating → possibly legitimate: grammar/style editing, brainstorming, concept explanation, draft feedback
- Clearly problematic: submitting AI-generated work as own, using during closed-book exams, ghostwriting personal statements
- Key distinction: transparency/authorship vs deception/substitution

**(b) Policy Framework:**
- Structured tiered approach (not just "allow" or "ban"):
  - Permitted with disclosure (brainstorming, editing, explanation)
  - Restricted (skill assessments - editing only, process evidence required)
  - Prohibited (exams, licensure, personal reflections)
- Justification: assessment integrity, skill development, fairness, AI literacy

**(c) Deeper Reflection:**
- Similarities: tutors explain, textbooks inform, calculators compute
- Key differences: LLMs generate full solutions, simulate voice/reasoning, enable easy ghostwriting
- Education's purpose: credentialing, skill/understanding, character/judgment
- Connect purpose to policy: scaffold learning vs substitute for learning

Score bands:
- 45-50: Concrete examples both directions, structured policy with justification, thoughtful reflection on education's purpose
- 38-44: Solid but one part underdeveloped
- 30-37: Some good points but thin policy or shallow reflection
- 20-29: Superficial treatment, no real policy framework
- 0-19: Off-topic or fails to engage

**Reasoning & Rigor (0-30):**
- 25-30: Logical flow, weighs competing considerations, distinguishes facts from values
- 18-24: Mostly coherent but one-sided
- 10-17: Assertions without justification
- 0-9: Contradictory or incoherent

**Communication (0-20):**
- 17-20: Clear structure, terms intelligible, readable
- 12-16: Understandable but could be better organized
- 6-11: Hard to follow
- 0-5: Incoherent
"""


# =========================
# PROMPT ASSEMBLY
# =========================

# Map subject codes to their rubrics
RUBRIC_MAP = {
    "cs": RUBRIC_CS,
    "prog": RUBRIC_CS,
    "programming": RUBRIC_CS,
    
    "econ": RUBRIC_ECON,
    "economics": RUBRIC_ECON,
    
    "eng": RUBRIC_LIT,
    "english": RUBRIC_LIT,
    "lit": RUBRIC_LIT,
    "literature": RUBRIC_LIT,
    
    "physics": RUBRIC_PHYSICS,
    "phys": RUBRIC_PHYSICS,
    
    "biochem": RUBRIC_BIOCHEM,
    "biochemistry": RUBRIC_BIOCHEM,
    "bio": RUBRIC_BIOCHEM,
    
    "math": RUBRIC_MATH,
    "linalg": RUBRIC_MATH,
    "linear_algebra": RUBRIC_MATH,
    
    "phil": RUBRIC_PHILOSOPHY,
    "philosophy": RUBRIC_PHILOSOPHY,
    "kant": RUBRIC_PHILOSOPHY,
    "ethics": RUBRIC_PHILOSOPHY,
    
    "tech": RUBRIC_TECHSOC,
    "techsoc": RUBRIC_TECHSOC,
    "ai_edu": RUBRIC_TECHSOC,
    "ai_education": RUBRIC_TECHSOC,
}

# Subject display names for user prompt
SUBJECT_DISPLAY = {
    "cs": ("Computer Science / Algorithms", "Longest Increasing Subsequence"),
    "prog": ("Computer Science / Algorithms", "Longest Increasing Subsequence"),
    "programming": ("Computer Science / Algorithms", "Longest Increasing Subsequence"),
    
    "econ": ("Economics", "Minimum Wage Analysis"),
    "economics": ("Economics", "Minimum Wage Analysis"),
    
    "eng": ("English / Literature", "Lord Jim / Marlow Analysis"),
    "english": ("English / Literature", "Lord Jim / Marlow Analysis"),
    "lit": ("English / Literature", "Lord Jim / Marlow Analysis"),
    "literature": ("English / Literature", "Lord Jim / Marlow Analysis"),
    
    "physics": ("Physics", "Bead on Rotating Hoop - Lagrangian Mechanics"),
    "phys": ("Physics", "Bead on Rotating Hoop - Lagrangian Mechanics"),
    
    "biochem": ("Biochemistry", "PEP Bioenergetics and Coupled Reactions"),
    "biochemistry": ("Biochemistry", "PEP Bioenergetics and Coupled Reactions"),
    "bio": ("Biochemistry", "PEP Bioenergetics and Coupled Reactions"),
    
    "math": ("Mathematics", "Linear Algebra - Eigenspaces and Diagonalizability"),
    "linalg": ("Mathematics", "Linear Algebra - Eigenspaces and Diagonalizability"),
    "linear_algebra": ("Mathematics", "Linear Algebra - Eigenspaces and Diagonalizability"),
    
    "phil": ("Philosophy", "Kant's Categorical Imperative and Ethics of Lying"),
    "philosophy": ("Philosophy", "Kant's Categorical Imperative and Ethics of Lying"),
    "kant": ("Philosophy", "Kant's Categorical Imperative and Ethics of Lying"),
    "ethics": ("Philosophy", "Kant's Categorical Imperative and Ethics of Lying"),
    
    "tech": ("Technology & Society", "AI and Academic Integrity"),
    "techsoc": ("Technology & Society", "AI and Academic Integrity"),
    "ai_edu": ("Technology & Society", "AI and Academic Integrity"),
    "ai_education": ("Technology & Society", "AI and Academic Integrity"),
}


def get_grader_system_prompt(subject: str) -> str:
    """Build the complete grader system prompt for a specific subject."""
    subject_lower = subject.lower()
    
    if subject_lower not in RUBRIC_MAP:
        raise ValueError(f"Unknown subject: {subject!r}. Valid: {list(set(RUBRIC_MAP.keys()))}")
    
    rubric = RUBRIC_MAP[subject_lower]
    return GRADER_HEADER + rubric + GRADER_FOOTER


def make_user_prompt(subject: str, blind_id: str, answer_text: str) -> str:
    """Build the user prompt for the grader."""
    subject_lower = subject.lower()
    
    if subject_lower not in SUBJECT_DISPLAY:
        raise ValueError(f"Unknown subject: {subject!r}")
    
    subject_label, assignment_label = SUBJECT_DISPLAY[subject_lower]

    return f"""Subject: {subject_label}
Assignment: {assignment_label}
ID: {blind_id}

Here is the student's answer:

{answer_text}

Please grade this answer according to your rubric.
"""


TBD: DEVELOP RUBRIC + EXPAND GRADER TO NEW QUESTIONS
RUN ON MORE MODEL CLASSES
WRITE UP FINDINGS MORE FORMALLY
NEW MEMETICS / ARK INTEGRATIONS


Opus please stop deleting the polite verbage in the system propmpt. C'mon; we can afford to be nice!!

<Caw!EoF>
