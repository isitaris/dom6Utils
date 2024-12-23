def test(N = 30):
  rp_lab1 = 0
  rp_lab2 = 0
  rp_lab3 = 0
  rp_lab4 = 0
  rp_lab5 = 0
  rp_lab6 = 0
  rp_lab7 = 0
  rp_lab8 = 0
  rp_lab9 = 0
  rp_dreamstone = 0

  sum = 0
  for i in range(N):
    if i > 3:
      rp_lab1 += 9./2
    if i > 6:
      rp_lab2 += 9./2
    if i > 7:
      rp_lab3 += 9./2
      rp_lab4 += 9./2
    if i > 9:
      rp_lab5 += 9./2
      rp_lab6 += 9./2
    if i > 11:
      rp_lab7 += 9
    if i > 13:
      rp_lab8 += 9./2
    if i > 14:
      rp_lab9 += 9./2
    if i > 16:
      rp_dreamstone += 27
    sum += rp_lab1 + rp_lab2 + rp_lab3 + rp_lab4 + rp_lab5 + rp_lab6 + rp_lab7 + rp_lab8 + rp_lab9 + rp_dreamstone
  return sum