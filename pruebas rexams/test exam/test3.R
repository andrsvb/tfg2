setwd(here::here("pruebas rexams", "test exam"))

library("exams")

myexam <- list(
  ### numer exercises:
  "deriv.Rmd",
  "fruit.Rmd",
  ### string exercise
  "function.Rmd"
)

set.seed(403)
ex1 <- exams2nops(myexam, n = 5,
  dir = "nops_pdf3", name = "demo", date = "2015-07-29",
  points = c(1, 1, 1, 2, 2, 3), showpoints = TRUE)