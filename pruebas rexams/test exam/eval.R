setwd(here::here("pruebas rexams", "test exam"))

ev1 <- nops_eval(
  register = "Exam-2015-07-29.csv",
  solutions = "nops_pdf/demo.rds",
  scans = Sys.glob("nops_scan/nops_scan_*.zip"),
  eval = exams_eval(partial = FALSE, negative = FALSE),
  interactive = FALSE
)
dir()