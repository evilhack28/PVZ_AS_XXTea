
/* WARNING: Restarted to delay deadcode elimination for space: stack */
/* LuaScriptMgr::LuaScriptMgr() */

void __thiscall LuaScriptMgr::LuaScriptMgr(LuaScriptMgr *this)

{
  int iVar1;
  lua_State *plVar2;
  LuaScriptMgr *pLVar3;
  int *piVar4;
  string asStack_d4 [12];
  string asStack_c8 [12];
  undefined4 local_bc;
  undefined4 uStack_b8;
  undefined4 uStack_b4;
  undefined4 local_ac;
  undefined4 uStack_a8;
  undefined4 uStack_a4;
  undefined4 local_a0;
  undefined4 local_9c;
  undefined4 uStack_98;
  undefined4 uStack_94;
  undefined4 local_90;
  undefined4 local_8c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  undefined4 local_80;
  _String_base<> a_Stack_7c [24];
  _String_base<> a_Stack_64 [24];
  string asStack_4c [24];
  string asStack_34 [24];
  int local_1c;
  
  local_1c = __stack_chk_guard;
  memset(&local_bc,0,0x10);
  local_9c = local_bc;
  uStack_98 = uStack_b8;
  uStack_94 = uStack_b4;
  *(undefined4 *)this = local_bc;
  *(undefined4 *)(this + 4) = uStack_b8;
  *(undefined4 *)(this + 8) = uStack_b4;
  *this = (LuaScriptMgr)0x0;
  *(undefined4 *)(this + 4) = 0;
  *(LuaScriptMgr **)(this + 8) = this;
  *(LuaScriptMgr **)(this + 0xc) = this;
  *(undefined4 *)(this + 0x10) = 0;
  memset(&local_ac,0,0x10);
  local_90 = local_a0;
  *(undefined4 *)(this + 0x18) = local_ac;
  *(undefined4 *)(this + 0x1c) = uStack_a8;
  *(undefined4 *)(this + 0x20) = uStack_a4;
  *(LuaScriptMgr **)(this + 0x20) = this + 0x18;
  *(LuaScriptMgr **)(this + 0x24) = this + 0x18;
  this[0x18] = (LuaScriptMgr)0x0;
  *(undefined4 *)(this + 0x1c) = 0;
  *(undefined4 *)(this + 0x28) = 0;
  memset(&local_8c,0,0x10);
  local_90 = local_80;
  *(undefined4 *)(this + 0x30) = local_8c;
  *(undefined4 *)(this + 0x34) = uStack_88;
  *(undefined4 *)(this + 0x38) = uStack_84;
  pLVar3 = this + 0x30;
  *pLVar3 = (LuaScriptMgr)0x0;
  *(LuaScriptMgr **)(this + 0x38) = pLVar3;
  *(LuaScriptMgr **)(this + 0x3c) = pLVar3;
  *(undefined4 *)(this + 0x34) = 0;
  *(undefined4 *)(this + 0x40) = 0;
  setXXTEAKeyAndSign("7ec34b808tk94hf1",0x10,"XXTEA",5);
  Instance = this;
  FUN_0079b000(a_Stack_7c,
               "\t\tfunction __G__TRACKBACK__(msg)\t\t\treturn debug.traceback(msg,2)\t\tend");
  iVar1 = cocos2d::CCLuaEngine::defaultEngine();
  piVar4 = *(int **)(iVar1 + 4);
  plVar2 = (lua_State *)piVar4[5];
  *(lua_State **)(this + 0x48) = plVar2;
  tolua_Pvzas_open(plVar2);
  DoString(asStack_d4);
  std::vector<>::~vector((vector<> *)asStack_d4);
  (**(code **)(*piVar4 + 0x1c))(piVar4,0x79c141);
  FUN_0079b000(a_Stack_64,"luaScript/main.lua");
  DoFile(asStack_c8);
  std::vector<>::~vector((vector<> *)asStack_c8);
  std::priv::_String_base<>::_M_deallocate_block(a_Stack_64);
  FUN_0079b000(asStack_4c,"protol");
  FUN_0079b000(asStack_34,"sendProtoMsg");
  RegisterLib(this,asStack_4c,asStack_34,(_func_int_lua_State_ptr *)&LAB_0079ac38_1);
  std::priv::_String_base<>::_M_deallocate_block((_String_base<> *)asStack_34);
  std::priv::_String_base<>::_M_deallocate_block((_String_base<> *)asStack_4c);
  std::priv::_String_base<>::_M_deallocate_block(a_Stack_7c);
  if (local_1c != __stack_chk_guard) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail(this);
  }
  return;
}

