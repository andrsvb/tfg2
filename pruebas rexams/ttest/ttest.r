setwd(here::here("pruebas rexams", "ttest"))

library("exams")

set.seed(403)
exams2html("ttest.Rmd", mathjax = TRUE, dir = '.')
set.seed(403)
exams2pdf("ttest.Rmd", dir = '.')

# there are different defined templates, and it should be easy to make a new template

# html templates
set.seed(403)
exams2html("ttest.Rmd", mathjax = TRUE, dir = "test_template", template = "plain")
set.seed(403)
exams2html("ttest.Rmd", mathjax = TRUE, dir = "test_template", template = "plain8")
set.seed(403)
exams2html("ttest.Rmd", mathjax = TRUE, dir = "test_template", template = "plain9")

# pdf templates
set.seed(403)
exams2pdf("ttest.Rmd", dir = "test_template", template = "exam")
set.seed(403)
exams2pdf("ttest.Rmd", dir = "test_template", template = "solution")
set.seed(403)
exams2pdf("ttest.Rmd", dir = "test_template", template = "plain")
set.seed(403)
exams2pdf("ttest.Rmd", dir = "test_template", template = "form")
set.seed(403)
exams2pdf("ttest.Rmd", dir = "test_template", template = "osolution")
set.seed(403)
exams2pdf("ttest.Rmd", dir = "test_template", template = "oexam")
set.seed(403)
exams2pdf("ttest.Rmd", dir = "test_template", template = "plain-highlight")
