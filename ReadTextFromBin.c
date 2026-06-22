
/* UtilityHelper::ReadTextFromBin(char const*) */

void __thiscall UtilityHelper::ReadTextFromBin(UtilityHelper *this,char *param_1)

{
  int *piVar1;
  uint uVar2;
  int *piVar3;
  undefined4 *puVar4;
  size_t sVar5;
  char *pcVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int local_91c;
  uint local_918;
  DBCFile aDStack_914 [8];
  int local_90c;
  int local_908;
  int local_900;
  int local_8fc;
  int local_8f4;
  int local_8f0;
  int local_8e8;
  int local_8e4;
  string asStack_8ac [20];
  undefined4 local_898;
  string asStack_894 [24];
  string asStack_87c [24];
  string asStack_864 [24];
  string asStack_84c [24];
  string asStack_834 [23];
  char acStack_81d [2049];
  int local_1c;
  
  local_1c = __stack_chk_guard;
  FUN_00570210(this,&DAT_01047bc4);
  local_91c = 0;
  FUN_00570210(asStack_8ac,param_1);
  piVar1 = (int *)cocos2d::CCFileUtils::sharedFileUtils();
  (**(code **)(*piVar1 + 0x18))(asStack_894,piVar1,param_1);
  std::string::operator=(asStack_8ac,asStack_894);
  std::priv::_String_base<>::_M_deallocate_block((_String_base<> *)asStack_894);
  piVar1 = (int *)cocos2d::CCFileUtils::sharedFileUtils();
  piVar1 = (int *)(**(code **)(*piVar1 + 0x10))(piVar1,local_898,&DAT_01048420,&local_91c);
  if (piVar1 != (int *)0x0) {
    uVar2 = strncmp((char *)piVar1,"XXTEA",5);
    piVar3 = piVar1;
    if (uVar2 == 0) {
      local_918 = uVar2;
      piVar3 = (int *)xxtea_decrypt((uchar *)((int)piVar1 + 5),local_91c - 5,
                                    (uchar *)"7ec34b808tk94hf1",0x10,&local_918);
      operator_delete__(piVar1);
    }
    if ((local_91c + 1U < 0x18) || (*piVar3 != -0x22443400)) {
      std::string::operator=((string *)this,(char *)piVar3);
    }
    else {
      DBC::DBCFile::DBCFile(aDStack_914,0);
      DBC::DBCFile::OpenFromMemory
                ((char *)aDStack_914,(char *)piVar3,(char *)((int)piVar3 + local_91c));
      FUN_00570210(asStack_87c,&DAT_01047bc4);
      for (uVar2 = 0; uVar2 < (uint)((local_908 - local_90c >> 3) * -0x55555555); uVar2 = uVar2 + 1)
      {
        std::string::operator+=(asStack_87c,(string *)(local_90c + uVar2 * 0x18));
        if (uVar2 < (local_908 - local_90c >> 3) * -0x55555555 - 1U) {
          std::string::operator+=(asStack_87c,"\t");
        }
      }
      std::string::operator+=(asStack_87c,"\n");
      FUN_00570210(asStack_864,&DAT_01047bc4);
      iVar9 = local_8fc - local_900 >> 2;
      for (iVar8 = 0; iVar8 < iVar9; iVar8 = iVar8 + 1) {
        iVar7 = *(int *)(iVar8 * 4 + local_900);
        pcVar6 = "FLOAT";
        if (iVar7 == 1) {
LAB_00573730:
          std::string::operator+=(asStack_864,pcVar6);
        }
        else {
          if (iVar7 == 2) {
            pcVar6 = "STRING";
            goto LAB_00573730;
          }
          if (iVar7 == 0) {
            pcVar6 = "INT";
            goto LAB_00573730;
          }
        }
        if (iVar8 < iVar9 + -1) {
          std::string::operator+=(asStack_864,"\t");
        }
      }
      std::string::operator+=(asStack_864,"\n");
      FUN_00570210(asStack_84c,&DAT_01047bc4);
      iVar9 = (local_8f0 - local_8f4 >> 3) * -0x55555555;
      for (iVar8 = 0; iVar8 < iVar9; iVar8 = iVar8 + 1) {
        std::string::operator+=(asStack_84c,(string *)(local_8f4 + iVar8 * 0x18));
        if (iVar8 < iVar9 + -1) {
          std::string::operator+=(asStack_84c,"\t");
        }
      }
      std::string::operator+=(asStack_84c,"\n");
      FUN_00570210(asStack_834,&DAT_01047bc4);
      for (iVar8 = 0; iVar8 < local_8e8; iVar8 = iVar8 + 1) {
        for (iVar9 = 0; iVar9 < local_8e4; iVar9 = iVar9 + 1) {
          iVar7 = *(int *)(iVar9 * 4 + local_900);
          if (iVar7 == 1) {
            puVar4 = (undefined4 *)DBC::DBCFile::Search_Posistion(aDStack_914,iVar8,iVar9);
            __extendsfdf2(*puVar4);
            snprintf(acStack_81d + 1,0x800,"%.2f");
            sVar5 = strlen(acStack_81d + 1);
            while (-1 < (int)(sVar5 - 1)) {
              if (acStack_81d[sVar5] != '0') {
                if (acStack_81d[sVar5] == '.') {
                  acStack_81d[sVar5] = '\0';
                }
                break;
              }
              acStack_81d[sVar5] = '\0';
              sVar5 = sVar5 - 1;
            }
          }
          else {
            if (iVar7 == 2) {
              puVar4 = (undefined4 *)DBC::DBCFile::Search_Posistion(aDStack_914,iVar8,iVar9);
              pcVar6 = "%s";
            }
            else {
              if (iVar7 != 0) goto LAB_0057383e;
              puVar4 = (undefined4 *)DBC::DBCFile::Search_Posistion(aDStack_914,iVar8,iVar9);
              pcVar6 = "%d";
            }
            snprintf(acStack_81d + 1,0x800,pcVar6,*puVar4);
          }
LAB_0057383e:
          std::string::operator+=(asStack_834,acStack_81d + 1);
          if (iVar9 < local_8e4 + -1) {
            pcVar6 = "\t";
          }
          else {
            pcVar6 = "\n";
          }
          std::string::operator+=(asStack_834,pcVar6);
        }
      }
      std::string::operator+=((string *)this,asStack_87c);
      std::string::operator+=((string *)this,asStack_864);
      std::string::operator+=((string *)this,asStack_84c);
      std::string::operator+=((string *)this,asStack_834);
      std::priv::_String_base<>::_M_deallocate_block((_String_base<> *)asStack_834);
      std::priv::_String_base<>::_M_deallocate_block((_String_base<> *)asStack_84c);
      std::priv::_String_base<>::_M_deallocate_block((_String_base<> *)asStack_864);
      std::priv::_String_base<>::_M_deallocate_block((_String_base<> *)asStack_87c);
      DBC::DBCFile::~DBCFile(aDStack_914);
    }
    if (piVar3 != (int *)0x0) {
      operator_delete__(piVar3);
    }
  }
  std::priv::_String_base<>::_M_deallocate_block((_String_base<> *)asStack_8ac);
  if (local_1c == __stack_chk_guard) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail(this);
}

