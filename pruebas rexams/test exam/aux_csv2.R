setwd(here::here("pruebas rexams", "test exam"))

# write needed csv with student info
write.table(data.frame(
  registration = c("1111111", "2222222", "3333333", "4444444", "5555555"),
  name = c("Uno Prueba", "Dos Prueba", "Tres Prueba", "Cuatro Prueba", "Cinco Prueba"),
  id = c("prueba1", "prueba2", "prueba3", "prueba4", "prueba5")
), file = "Exam-2024-03-13.csv", sep = ";", quote = FALSE, row.names = FALSE)