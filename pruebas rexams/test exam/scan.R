setwd(here::here("pruebas rexams", "test exam"))

# copy example images from exams library
img <- dir(system.file("nops", package = "exams"), pattern = "nops_scan",
  full.names = TRUE)
dir.create("nops_scan")
file.copy(img, to = "nops_scan")

# scan example images
nops_scan(dir = "nops_scan")

# test with non checkbox results failed
# nops_scan(dir = "nops_scan2")