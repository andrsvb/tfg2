setwd(here::here("pruebas rexams", "first steps"))

library("exams")
exams_skeleton(markup = "markdown",
    writer = c("exams2html", "exams2pdf", "exams2moodle"))