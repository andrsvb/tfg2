library("exams")

set.seed(403)
exams2html("dist.Rmd", mathjax = TRUE)
set.seed(403)
exams2pdf("dist.Rmd")