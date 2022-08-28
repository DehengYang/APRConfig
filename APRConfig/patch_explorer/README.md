# Fake Plausible Patch Analysis

All scripts for our analysis of the fake plausible patches and the associated result data are publicly available here.

P.S. Interestingly, we observe that two patches (Nopol for Lang_58 and Arja for Lang_51) fail to compile when evaluated with Defects4J command. Actually, the two patches are plausible patches, as Nopol and Arja use different test runners rather than Defects4J command to compile patch and run test validation. When setting `compile.source = 1.5` and `compile.target = 1.5` in `default.properties` file of the buggy program folder, the Defects4J command could successfully compile and pass all tests for the two patches.
