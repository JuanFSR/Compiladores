; ModuleID = "modulo_geracao_cod.bc"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

declare void @"escrevaInteiro"(i32 %".1") 

declare void @"escrevaFlutuante"(float %".1") 

declare i32 @"leiaInteiro"() 

declare float @"leiaFlutuante"() 

define i32 @"soma"(i32 %"a", i32 %"b") 
{
entry:
  br label %"exit"
exit:
  %".5" = add i32 %"a", %"b"
  ret i32 %".5"
}

define i32 @"main"() 
{
entry:
  %"a" = alloca i32, align 4
  %"b" = alloca i32, align 4
  %"c" = alloca i32, align 4
  %".2" = call i32 @"leiaInteiro"()
  store i32 %".2", i32* %"a", align 4
  %".4" = call i32 @"leiaInteiro"()
  store i32 %".4", i32* %"b", align 4
  %".6" = load i32, i32* %"a"
  %".7" = load i32, i32* %"b"
  %".8" = call i32 @"soma"(i32 %".6", i32 %".7")
  store i32 %".8", i32* %"c"
  %".10" = load i32, i32* %"c"
  call void @"escrevaInteiro"(i32 %".10")
  br label %"exit"
exit:
  %".13" = load i32, i32* %"b"
  ret i32 %".13"
}
