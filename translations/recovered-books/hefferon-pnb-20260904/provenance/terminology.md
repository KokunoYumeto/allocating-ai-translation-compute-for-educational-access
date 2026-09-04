# Shahmukhi language and mathematical terminology

Native Pakistani Punjabi/Shahmukhi is the primary explanatory language. Urdu
and English assistance occupy separately labeled glossary columns; neither is
presented as a substitute for Punjabi.

The inherited prose canon contains twelve short loci in three essays by Jamil
Ahmad Pal, with exact quotations, URLs and application notes in
`canon/examples.json`. The retrieved snapshots were checked again during
recovery. These examples support Punjabi constructions such as *can*, *should*,
ordered prose, reminders and reasons. They are not linear-algebra authorities.
Full essay snapshots are not included in this public package.

A bounded primary-source search did not establish a suitable native Pakistani
Shahmukhi linear-algebra terminology reference. This is a limitation of the
search, not a claim that none exists. The [University of the Punjab's Institute
of Punjabi and Cultural Studies](https://ipcs.edu.pk/website/about) identifies
Shahmukhi as its teaching script, but does not attest the technical terms here.
The [Lahore Punjabi-Punjabi dictionary catalogue](https://dsal.uchicago.edu/dictionaries/salah-ud-din/)
is a relevant lexicographic candidate, not a retrieved mathematical definition.
An author's provisional Gurmukhi-to-Shahmukhi transcription was not accepted as
native Pakistani orthographic evidence.

Official Urdu/English school materials were considered only as bridge evidence:
[NCERT's Urdu mathematics listing](https://www.ncert.nic.in/pdf/BookletClass8.pdf),
[BISE Lahore model papers](https://www.biselahore.com/downloads/Model%20Papers/Matric/ModelPapers_9th.pdf),
and [eLearn.Punjab](https://www.elearn.gov.pk/). Some printed pages could not be
retrieved or visually verified; indexed snippets are not certified printed
quotations. No term in this package is labeled standardized solely on those
results. The glossary's Urdu alternatives are provisional explanatory help,
not an official terminology standard.

## Meaning-based decisions

- Preserve source-bound symbols and exact mathematical distinctions; specialist
  Punjabi labels remain provisional.
- A system's solution must satisfy every equation simultaneously.
- The coordinate-vector explanation is limited to the elementary examples;
  abstract vector spaces are not reduced to physical arrows or number lists.
- Span means all finite linear combinations, not one combination.
- Hefferon defines a basis as an **ordered sequence** that is independent and
  spans the space. Source `src/vs/vs3.tex:19-42` explicitly says order matters.
- The label `مرکب عدد` is explicitly paired with *complex number*, `a+bi`, and
  `i²=-1`; it is not confused with a composite integer. Urdu assistance uses a
  separately labeled provisional synonym.
- The inherited notation row's degree-n polynomial wording stays unchanged;
  its separate note correctly points to degree n **or less**, as defined in
  `src/vs/vs1.tex:454-459`.
- The contents retain `کثیرحدی`, matching the recovered opening terminology.
  Factoring is an action; nilpotence specifies a positive-integer power;
  Gram-Schmidt's label makes mutual orthogonality explicit.

These choices are reversible and source-bound. The package does not claim
community-wide terminology acceptance, native-speaker certification or a
learner-outcome study. Those missing claims are not publication holds.
