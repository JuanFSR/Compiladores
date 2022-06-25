; ModuleID = "modulo_geracao_cod.bc"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

declare void @"escrevaInteiro"(i32 %".1") 

declare void @"escrevaFlutuante"(float %".1") 

declare i32 @"leiaInteiro"() 

declare float @"leiaFlutuante"() 

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
  %".6" = load i32, i32* %"b"
  call void @"escrevaInteiro"(i32 %".6")
  br label %"exit"
exit:
  ret i32 0
}
