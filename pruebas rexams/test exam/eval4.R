setwd(here::here("pruebas rexams", "test exam", "nops_eval4"))

ev1 <- nops_eval(
  register = "../Exam-2024-03-13.csv",
  solutions = "../nops_pdf4/demo.rds",
  scans = Sys.glob("../nops_scan4/nops_scan_*.zip"),
  eval = exams_eval(partial = TRUE, negative = TRUE),
  interactive = TRUE
)
dir()