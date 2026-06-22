
/* UtilityHelper::DBCFile_OpenFromMemory(DBC::DBCFile&, char const*) */

void UtilityHelper::DBCFile_OpenFromMemory(DBCFile *param_1,char *param_2)

{
  int *piVar1;
  char *__s1;
  uint uVar2;
  char *pcVar3;
  int iVar4;
  undefined4 uVar5;
  int local_54;
  uint local_50;
  string asStack_4c [20];
  undefined4 local_38;
  string asStack_34 [24];
  int local_1c;
  
  local_1c = __stack_chk_guard;
  FUN_00570210(asStack_4c);
  piVar1 = (int *)cocos2d::CCFileUtils::sharedFileUtils();
  (**(code **)(*piVar1 + 0x18))(asStack_34,piVar1,param_2);
  std::string::operator=(asStack_4c,asStack_34);
  std::priv::_String_base<>::_M_deallocate_block((_String_base<> *)asStack_34);
  local_54 = 0;
  piVar1 = (int *)cocos2d::CCFileUtils::sharedFileUtils();
  __s1 = (char *)(**(code **)(*piVar1 + 0x10))(piVar1,local_38,&DAT_01048420,&local_54);
  if (__s1 == (char *)0x0) {
    uVar5 = 0;
  }
  else {
    uVar2 = strncmp(__s1,"XXTEA",5);
    pcVar3 = __s1;
    if (uVar2 == 0) {
      local_50 = uVar2;
      pcVar3 = (char *)xxtea_decrypt((uchar *)(__s1 + 5),local_54 - 5,(uchar *)"7ec34b808tk94hf1",
                                     0x10,&local_50);
      operator_delete__(__s1);
    }
    DBC::DBCFile::OpenFromMemory((char *)param_1,pcVar3,pcVar3 + local_54);
    if ((*(int *)(param_1 + 0x30) < 1) || (*(int *)(param_1 + 0x2c) < 1)) {
      iVar4 = cc_assert_script_compatible("error read file");
      if (iVar4 == 0) {
        cocos2d::CCLog("Assert failed: %s","error read file");
      }
      __android_log_print(6,"cocos2d-x assert","%s function:%s line:%d",
                          "jni/../../Classes/Auxiliary/UtilityHelper.cpp","DBCFile_OpenFromMemory",
                          0x30b);
    }
    uVar5 = 1;
    if (pcVar3 != (char *)0x0) {
      operator_delete__(pcVar3);
    }
  }
  std::priv::_String_base<>::_M_deallocate_block((_String_base<> *)asStack_4c);
  if (local_1c != __stack_chk_guard) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail(uVar5);
  }
  return;
}

