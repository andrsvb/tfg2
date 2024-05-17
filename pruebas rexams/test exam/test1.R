setwd(here::here("pruebas rexams", "test exam"))

library("exams")

myexam <- list(
  "tstat2.Rnw",
  "ttest.Rnw",
  "relfreq.Rnw",
  "anova.Rnw",
  c("boxplots.Rnw", "scatterplot.Rnw"),
  "cholesky.Rnw"
)

set.seed(403)
ex1 <- exams2nops(myexam, n = 2,
  dir = "nops_pdf", name = "demo", date = "2015-07-29",
  points = c(1, 1, 1, 2, 2, 3), showpoints = TRUE)