#let font_size_zh = (
  ChuHao: 42pt,
  XiaoChu: 36pt,
  YiHao: 26pt,
  XiaoYi: 24pt,
  ErHao: 22pt,
  XiaoEr: 18pt,
  SanHao: 16pt,
  XiaoSan: 15pt,
  SiHao: 14pt,
  ZhongSi: 13pt,
  XiaoSi: 12pt,
  WuHao: 10.5pt,
  XiaoWu: 9pt,
  LiuHao: 7.5pt,
  XiaoLiu: 6.5pt,
  QiHao: 5.5pt,
  XiaoQi: 5pt,
)

#let font_zh = (
  // 宋体，属于「有衬线字体」，一般可以等同于英文中的 Serif Font
  SongTi: ("Times New Roman","Songti SC"),
  // 黑体，属于「无衬线字体」，一般可以等同于英文中的 Sans Serif Font
  HeiTi: ("Arial", "SimHei"),
  // 楷体
  KaiTi: ("Times New Roman", "KaiTi", "Kaiti SC", "STKaiti", "FZKai-Z03S", "Noto Serif CJK SC"),
  // 仿宋
  FangSong: ("Times New Roman", "FangSong", "FangSong SC", "STFangSong", "FZFangSong-Z02S", "Noto Serif CJK SC"),
  // 等宽字体，用于代码块环境，一般可以等同于英文中的 Monospaced Font
  Monospaced: ("Courier New","SimHei"),
)

// latex like section, subsection, subsub
//counters
#let TheSection=counter("the_section")
#let TheSubSection=counter("the_sub_section")
#let TheSubSub=counter("the_sub_sub_section")
//section
#let Section(body,inc:true)={
  set text(font: font_zh.HeiTi, size: font_size_zh.SanHao)
  //set align(center)
  v(1*(font_size_zh.SanHao))
  if inc{
    TheSection.step()
    TheSubSection.update(0)
    TheSubSub.update(0)
    context TheSection.display("一、")
  }
  context body
  parbreak()
}
#let SubSection(body,inc:true)={
  set text(font: font_zh.HeiTi, size: font_size_zh.SiHao)
  v(1*(font_size_zh.SiHao))
  if inc{
    TheSubSection.step()
    TheSubSub.update(0)
    context TheSection.display("1.")
    context TheSubSection.display("1  ")
  }
  context body
  parbreak()
  v(-3pt)
}
#let SubSub(body,inc:true)={
  set text(font: font_zh.HeiTi, size: font_size_zh.XiaoSi)
  v(0.8*(font_size_zh.XiaoSi))
  if inc{
    TheSubSub.step()
    context TheSection.display("1.")
    context TheSubSection.display("1.")
    context TheSubSub.display("1 ")
  }
  context body
  parbreak()
  v(-3pt)
}

// new paragraph with parskip
#let PARSKIP=0.5*(font_size_zh.XiaoSi)
#let MYPAR(parskip: PARSKIP)={
  parbreak()
  //v(PARSKIP)
  //parbreak()
  h(0.74cm)
}