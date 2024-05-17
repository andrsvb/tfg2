setwd(here::here("pruebas rexams", "test exam"))

ev1 <- nops_eval(
  register = "Exam-2024-03-13.csv",
  solutions = "nops_pdf2/demo.rds",
  scans = Sys.glob("nops_scan2/nops_scan_*.zip"),
  eval = exams_eval(partial = FALSE, negative = FALSE),
  interactive = FALSE
)
dir()