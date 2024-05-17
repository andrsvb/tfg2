setwd(here::here("pruebas rexams", "test exam"))

library("exams")

myexam <- list(
  ### numer exercises:
  "deriv.Rmd",
  "fruit.Rmd",
  ### single choice exercises:
  "tstat2.Rnw",
  "ttest.Rnw",
  ### multiple choice exercises:
  # randomizes which exercise is in which exam: some have boxplot some have scatterplot
  c("boxplots.Rnw", "scatterplot.Rnw"),
  ### string exercise
  "function.Rmd"
  # cloze excerzises throw error: "dist2.Rmd"
)

set.seed(403)
ex1 <- exams2nops(myexam, n = 5,
  dir = "nops_pdf2", name = "demo", date = "2015-07-29",
  points = c(1, 1, 1, 2, 2, 3), showpoints = TRUE)