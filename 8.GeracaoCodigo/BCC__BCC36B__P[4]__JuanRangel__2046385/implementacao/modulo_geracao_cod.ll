; ModuleID = "modulo_geracao_cod.bc"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

declare void @"escrevaInteiro"(i32 %".1") 

declare void @"escrevaFlutuante"(float %".1") 

declare i32 @"leiaInteiro"() 

declare float @"leiaFlutuante"() 

@"n" = common global i32 0, align 4
@"soma" = common global i32 0, align 4
define i32 @"main"() 
{
entry:
  store i32 10, i32* @"n"
  store i32 0, i32* @"soma"
  %".4" = load i32, i32* @"soma"
  call void @"escrevaInteiro"(i32 %".4")
  br label %"exit"
exit:
  ret i32 0
}
