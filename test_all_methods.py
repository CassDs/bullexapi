"""Script completo de auditoria e teste de todos os métodos da bullexapi (Modo PRACTICE)."""

import os
import sys
import time
import threading
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Garante que o pacote local em Api/Bullex seja importado
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from bullexapi.stable_api import Bullex
import bullexapi.constants as OP_code


def load_env(env_path: Path) -> dict:
    env_vars = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env_vars[k.strip()] = v.strip().strip('"').strip("'")
    return env_vars


def run_with_timeout(func, timeout_sec=15.0):
    """Executa func() em uma thread com timeout para detectar métodos que travam em loop infinito."""
    result_box = {"status": "TIMEOUT", "value": None, "error": None, "elapsed_ms": 0}
    t0 = time.time()

    def target():
        try:
            val = func()
            result_box["value"] = val
            result_box["status"] = "OK"
        except Exception as e:
            result_box["error"] = f"{type(e).__name__}: {e}"
            result_box["status"] = "EXCEPTION"
        finally:
            result_box["elapsed_ms"] = int((time.time() - t0) * 1000)

    th = threading.Thread(target=target, daemon=True)
    th.start()
    th.join(timeout=timeout_sec)
    if result_box["status"] == "TIMEOUT":
        result_box["elapsed_ms"] = int((time.time() - t0) * 1000)
    return result_box


def pick_open_active(api: Bullex, kind="turbo"):
    """Seleciona um ativo aberto no momento (com schedule válido) usando get_all_init_v2()."""
    try:
        init_v2 = api.get_all_init_v2()
        now_ts = api.get_server_timestamp()
        if init_v2:
            actives = init_v2.get(kind, {}).get("actives", {})
            if not actives and kind == "turbo":
                actives = init_v2.get("blitz", {}).get("actives", {})
            for aid, info in actives.items():
                if info.get("enabled") and not info.get("is_suspended"):
                    sched = info.get("schedule") or []
                    if sched and not any(s[0] <= now_ts <= s[1] for s in sched if isinstance(s, (list, tuple)) and len(s) >= 2):
                        continue
                    name = str(info.get("name", "")).split(".", 1)[-1]
                    if name:
                        OP_code.ACTIVES[name] = int(aid)
                        exp_list = info.get("option", {}).get("expiration_times") or [30]
                        return name, int(aid), exp_list[0]
    except Exception:
        pass
    return "EURUSD", OP_code.ACTIVES.get("EURUSD", 1861), 30


def main():
    env = load_env(BASE_DIR / ".env")
    email = env.get("BULLEX_EMAIL") or env.get("IQ_EMAIL") or os.environ.get("BULLEX_EMAIL", "")
    password = env.get("BULLEX_PASSWORD") or env.get("IQ_PASSWORD") or os.environ.get("BULLEX_PASSWORD", "")

    if not email or not password or "seu_email_aqui" in email:
        print("⚠️  Preencha suas credenciais da Bullex no arquivo Api/Bullex/.env (BULLEX_EMAIL e BULLEX_PASSWORD).")
        sys.exit(1)

    print("=" * 80)
    print(f"🚀 INICIANDO BATERIA DE TESTES DA BULLEXAPI ({email})")
    print("=" * 80)

    api = Bullex(email, password)
    results = []

    def record(category, method_name, timeout_sec, fn, validator=None):
        print(f"⏳ Testando {method_name:<38} ... ", end="", flush=True)
        res = run_with_timeout(fn, timeout_sec=timeout_sec)
        status = res["status"]
        detail = ""
        if status == "OK":
            val = res["value"]
            if validator is not None:
                ok_val, msg_val = validator(val)
                if not ok_val:
                    status = "FAIL_RETURN"
                    detail = msg_val
                else:
                    detail = msg_val
            else:
                detail = str(val)[:80]
        elif status == "EXCEPTION":
            detail = res["error"]
        else:
            detail = f"Travou em loop infinito (> {timeout_sec}s)"

        icon = "✅" if status == "OK" else "❌"
        print(f"{icon} {status} ({res['elapsed_ms']} ms) — {detail}")
        results.append({
            "category": category,
            "method": method_name,
            "status": status,
            "elapsed_ms": res["elapsed_ms"],
            "detail": detail,
        })
        return res["value"] if status == "OK" else None

    # 1. CONEXÃO & AUTENTICAÇÃO
    conn_res = record(
        "1. Conexão",
        "connect()",
        20.0,
        lambda: api.connect(),
        lambda v: (isinstance(v, tuple) and v[0] is True, f"check={v[0]}, reason={v[1]}"),
    )
    if not conn_res or conn_res[0] is not True:
        print("\n❌ Não foi possível autenticar na Bullex. Verifique o arquivo Api/Bullex/.env ou 2FA.")
        sys.exit(1)

    record("1. Conexão", "check_connect()", 5.0, lambda: api.check_connect(), lambda v: (v is True, f"connected={v}"))
    record("1. Conexão", "get_server_timestamp()", 5.0, lambda: api.get_server_timestamp(), lambda v: (isinstance(v, (int, float)) and v > 1000000000, f"ts={v}"))
    record("1. Conexão", "get_remaning(1)", 5.0, lambda: api.get_remaning(1), lambda v: (isinstance(v, (int, float)), f"remaining={v}s"))

    # 2. CONTA, SALDO E MODO TREINAMENTO (PRACTICE)
    record("2. Conta & Saldo", "change_balance('PRACTICE')", 10.0, lambda: api.change_balance("PRACTICE"), lambda v: (True, "Executado"))
    mode = record("2. Conta & Saldo", "get_balance_mode()", 10.0, lambda: api.get_balance_mode(), lambda v: (v == "PRACTICE", f"mode={v}"))
    if mode != "PRACTICE":
        print(f"\n🛑 ABORTANDO COMPRAS POR SEGURANÇA: Conta não está em PRACTICE (modo atual: {mode})")
        sys.exit(1)

    record("2. Conta & Saldo", "get_balance_id()", 5.0, lambda: api.get_balance_id(), lambda v: (v is not None, f"balance_id={v}"))
    record("2. Conta & Saldo", "get_balances()", 10.0, lambda: api.get_balances(), lambda v: (isinstance(v, dict) and "msg" in v, f"qtd_contas={len(v.get('msg', []))}"))
    record("2. Conta & Saldo", "get_balance()", 10.0, lambda: api.get_balance(), lambda v: (isinstance(v, (int, float)), f"saldo={v}"))
    record("2. Conta & Saldo", "get_currency()", 10.0, lambda: api.get_currency(), lambda v: (bool(v), f"moeda={v}"))
    record("2. Conta & Saldo", "get_profile_ansyc()", 10.0, lambda: api.get_profile_ansyc(), lambda v: (isinstance(v, dict), f"user_id={v.get('user_id')}"))
    record("2. Conta & Saldo", "reset_practice_balance()", 10.0, lambda: api.reset_practice_balance(), lambda v: (v is not None, f"resp={v}"))

    # 3. INICIALIZAÇÃO, ATIVOS & PAYOUTS
    record("3. Ativos & Payouts", "get_all_ACTIVES_OPCODE()", 5.0, lambda: api.get_all_ACTIVES_OPCODE(), lambda v: (isinstance(v, dict) and len(v) > 0, f"ativos={len(v)}"))
    record("3. Ativos & Payouts", "get_all_init_v2()", 25.0, lambda: api.get_all_init_v2(), lambda v: (isinstance(v, dict) and ("turbo" in v or "binary" in v), f"keys={list(v.keys()) if isinstance(v, dict) else v}"))
    record("3. Ativos & Payouts", "get_all_init() [v1 legado]", 12.0, lambda: api.get_all_init(), lambda v: (isinstance(v, dict) and v.get("isSuccessful") is True, "OK"))
    record("3. Ativos & Payouts", "get_ALL_Binary_ACTIVES_OPCODE()", 12.0, lambda: api.get_ALL_Binary_ACTIVES_OPCODE(), lambda v: (True, f"OP_code.ACTIVES={len(OP_code.ACTIVES)}"))
    record("3. Ativos & Payouts", "get_binary_option_detail()", 12.0, lambda: api.get_binary_option_detail(), lambda v: (isinstance(v, dict) and len(v) > 0, f"detalhes={len(v)} ativos"))
    record("3. Ativos & Payouts", "get_all_profit()", 12.0, lambda: api.get_all_profit(), lambda v: (isinstance(v, dict) and len(v) > 0, f"profits={len(v)} ativos"))
    record("3. Ativos & Payouts", "get_digital_underlying_list_data()", 15.0, lambda: api.get_digital_underlying_list_data(), lambda v: (isinstance(v, dict) and "underlying" in v, f"digital_ativos={len(v.get('underlying', []))}"))
    record("3. Ativos & Payouts", "get_instruments('crypto')", 12.0, lambda: api.get_instruments("crypto"), lambda v: (isinstance(v, dict) and "instruments" in v, f"crypto={len(v.get('instruments', []))}"))
    record("3. Ativos & Payouts", "get_instruments('forex')", 12.0, lambda: api.get_instruments("forex"), lambda v: (isinstance(v, dict) and "instruments" in v, f"forex={len(v.get('instruments', []))}"))
    record("3. Ativos & Payouts", "get_instruments('cfd')", 20.0, lambda: api.get_instruments("cfd"), lambda v: (isinstance(v, dict) and "instruments" in v, f"cfd={len(v.get('instruments', []))}"))
    record("3. Ativos & Payouts", "update_ACTIVES_OPCODE()", 15.0, lambda: api.update_ACTIVES_OPCODE(), lambda v: (len(OP_code.ACTIVES) > 500, f"OP_code.ACTIVES={len(OP_code.ACTIVES)}"))
    record("3. Ativos & Payouts", "get_all_open_time()", 20.0, lambda: api.get_all_open_time(), lambda v: (isinstance(v, dict) and "turbo" in v, f"modalidades={list(v.keys())}"))

    open_active, open_active_id, _ = pick_open_active(api, "turbo")
    blitz_active, _, blitz_exp = pick_open_active(api, "blitz")
    digital_active = open_active
    try:
        now_ts = api.get_server_timestamp()
        du = api.get_digital_underlying_list_data()
        for item in (du or {}).get("underlying", []):
            if not item.get("is_suspended") and any(s.get("open", 0) <= now_ts <= s.get("close", 0) for s in item.get("schedule", [])):
                u_name = item.get("underlying")
                if u_name and item.get("active_id"):
                    OP_code.ACTIVES[u_name] = int(item["active_id"])
                    digital_active = u_name
                    break
    except Exception:
        pass
    print(f"ℹ️  Ativo aberto selecionado para testes de mercado/ordens: {open_active} (id={open_active_id})")

    record("3. Ativos & Payouts", f"get_financial_information({open_active_id})", 10.0, lambda: api.get_financial_information(open_active_id), lambda v: (isinstance(v, dict), f"status={v.get('status') if isinstance(v, dict) else v}"))
    record("3. Ativos & Payouts", f"get_name_by_activeId({open_active_id})", 10.0, lambda: api.get_name_by_activeId(open_active_id), lambda v: (bool(v), f"name={v}"))
    record("3. Ativos & Payouts", f"get_digital_payout('{digital_active}')", 8.0, lambda: api.get_digital_payout(digital_active, seconds=5), lambda v: (isinstance(v, int) and v > 0, f"payout={v}%"))
    record("3. Ativos & Payouts", f"get_blitz_payout('{open_active}')", 10.0, lambda: api.get_blitz_payout(open_active), lambda v: (isinstance(v, int) and v > 0, f"payout={v}%"))

    # 4. CANDLES, STREAMS, HUMOR & INDICADORES
    record("4. Candles & Streams", f"get_candles('{open_active}', 60, 10)", 12.0, lambda: api.get_candles(open_active, 60, 10, time.time()), lambda v: (isinstance(v, list) and len(v) > 0, f"velas={len(v)}, close={v[-1].get('close')}"))
    record("4. Candles & Streams", f"start_candles_stream('{open_active}', 60)", 12.0, lambda: api.start_candles_stream(open_active, 60, 10), lambda v: (True, "stream iniciado"))
    record("4. Candles & Streams", f"get_realtime_candles('{open_active}', 60)", 5.0, lambda: api.get_realtime_candles(open_active, 60), lambda v: (isinstance(v, dict) and len(v) > 0, f"realtime_velas={len(v)}"))
    record("4. Candles & Streams", f"stop_candles_stream('{open_active}', 60)", 8.0, lambda: api.stop_candles_stream(open_active, 60), lambda v: (True, "stream parado"))
    record("4. Candles & Streams", f"start_mood_stream('{open_active}')", 10.0, lambda: api.start_mood_stream(open_active), lambda v: (True, "mood stream iniciado"))
    record("4. Candles & Streams", f"get_traders_mood('{open_active}')", 5.0, lambda: api.get_traders_mood(open_active), lambda v: (isinstance(v, (int, float)), f"mood={v}"))
    record("4. Candles & Streams", f"stop_mood_stream('{open_active}')", 5.0, lambda: api.stop_mood_stream(open_active), lambda v: (True, "mood stream parado"))
    record("4. Candles & Streams", f"get_technical_indicators('{open_active}')", 10.0, lambda: api.get_technical_indicators(open_active), lambda v: (v is not None, f"tipo={type(v).__name__}"))

    # 5. ORDENS & HISTÓRICO (ESTRITAMENTE EM MODO PRACTICE)
    assert api.get_balance_mode() == "PRACTICE", "Segurança: precisa estar em PRACTICE!"

    record("5. Ordens & Histórico (PRACTICE)", "get_optioninfo(5)", 10.0, lambda: api.get_optioninfo(5), lambda v: (isinstance(v, dict), f"isSuccessful={v.get('msg', {}).get('isSuccessful')}"))
    record("5. Ordens & Histórico (PRACTICE)", "get_optioninfo_v2(5)", 10.0, lambda: api.get_optioninfo_v2(5), lambda v: (isinstance(v, dict) and "msg" in v, f"closed={len(v.get('msg', {}).get('closed_options', []))}"))
    record("5. Ordens & Histórico (PRACTICE)", "get_position_history('turbo-option')", 10.0, lambda: api.get_position_history("turbo-option"), lambda v: (isinstance(v, tuple) and v[0] is True, f"ok={v[0]}"))
    record("5. Ordens & Histórico (PRACTICE)", "get_position_history_v2('turbo-option')", 10.0, lambda: api.get_position_history_v2("turbo-option", 5, 0, 0, 0), lambda v: (isinstance(v, tuple) and v[0] is True, f"ok={v[0]}, qtd={len(v[1].get('positions', [])) if isinstance(v[1], dict) else 0}"))

    buy_res = record(
        "5. Ordens & Histórico (PRACTICE)",
        f"buy(2, '{open_active}', 'call', 1)",
        10.0,
        lambda: api.buy(2, open_active, "call", 1),
        lambda v: (isinstance(v, tuple) and v[0] is True, f"ok={v[0]}, order_id={v[1]}"),
    )
    if isinstance(buy_res, tuple) and buy_res[0] is True and buy_res[1]:
        oid = buy_res[1]
        record("5. Ordens & Histórico (PRACTICE)", f"sell_option({oid})", 10.0, lambda: api.sell_option(oid), lambda v: (v is not None, f"resp={str(v)[:60]}"))

    record(
        "5. Ordens & Histórico (PRACTICE)",
        f"buy_blitz('{blitz_active}', 2, 'call', {blitz_exp})",
        12.0,
        lambda: api.buy_blitz(blitz_active, 2, "call", blitz_exp),
        lambda v: (isinstance(v, tuple) and v[0] is True, f"ok={v[0]}, id_or_msg={v[1]}"),
    )

    record(
        "5. Ordens & Histórico (PRACTICE)",
        f"buy_digital_spot_v2('{digital_active}', 2, 'call', 1)",
        12.0,
        lambda: api.buy_digital_spot_v2(digital_active, 2, "call", 1),
        lambda v: (isinstance(v, tuple) and v[0] is True, f"ok={v[0]}, id_or_msg={v[1]}"),
    )

    # 6. VALIDAÇÃO DE MERCADOS ABERTOS E MULTI-MOEDAS PARA COMPRA (PRACTICE)
    open_map = api.get_all_open_time()
    print("\n" + "-" * 80)
    print("🌎 AUDITORIA DE MERCADOS ABERTOS POR MODALIDADE (get_all_open_time):")
    for mod in ("turbo", "binary", "blitz", "digital", "forex", "crypto", "cfd"):
        mod_dict = open_map.get(mod, {})
        open_list = [k for k, v in mod_dict.items() if v.get("open") is True]
        print(f"  • {mod.upper():<8}: {len(open_list):>4} abertos de {len(mod_dict):>4} ativos | Exemplos: {open_list[:6]}")
    print("-" * 80)

    open_turbo_currencies = [
        k for k, v in open_map.get("turbo", {}).items()
        if v.get("open") is True and any(p in k for p in ("EUR", "USD", "GBP", "JPY", "AUD", "CAD", "CHF", "BTC", "ETH"))
    ][:3]
    for curr_pair in open_turbo_currencies:
        record(
            "6. Multi-Moedas Abertas (PRACTICE)",
            f"buy(2, '{curr_pair}', 'call', 1) [Turbo]",
            8.0,
            lambda c=curr_pair: api.buy(2, c, "call", 1),
            lambda v: (isinstance(v, tuple) and v[0] is True, f"ok={v[0]}, order_id={v[1]}"),
        )

    open_digital_currencies = [
        k for k, v in open_map.get("digital", {}).items()
        if v.get("open") is True and any(p in k for p in ("EUR", "USD", "GBP", "JPY", "AUD", "CAD"))
    ][:3]
    for curr_pair in open_digital_currencies:
        record(
            "6. Multi-Moedas Abertas (PRACTICE)",
            f"buy_digital_spot_v2('{curr_pair}', 2, 'put', 1)",
            8.0,
            lambda c=curr_pair: api.buy_digital_spot_v2(c, 2, "put", 1),
            lambda v: (isinstance(v, tuple) and v[0] is True, f"ok={v[0]}, order_id={v[1]}"),
        )

    # 7. VALIDAÇÃO DE ATIVOS SEM OTC (MERCADO REAL / NON-OTC)
    const_path = BASE_DIR / "bullexapi" / "constants.py"
    import json as _json
    const_path.write_text('"""Module for Bullex API constants."""\n\nACTIVES = ' + _json.dumps(OP_code.ACTIVES, indent=4) + "\n", encoding="utf-8")

    for non_otc_pair in ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "BTCUSD", "ETHUSD"):
        record(
            "7. Mercado Sem OTC (Candles & IDs)",
            f"get_candles('{non_otc_pair}', 60, 5) [id={OP_code.ACTIVES.get(non_otc_pair)}]",
            8.0,
            lambda p=non_otc_pair: api.get_candles(p, 60, 5, time.time()),
            lambda v: (isinstance(v, list) and len(v) == 5, f"velas={len(v)}, close={v[-1].get('close')}"),
        )

    open_non_otc_list = []
    for mod_name, exp_m in (("binary", 15), ("turbo", 1), ("blitz", 1)):
        for k, v in open_map.get(mod_name, {}).items():
            if v.get("open") is True and "OTC" not in k.upper() and not k.endswith("-op"):
                if not any(x[0] == k for x in open_non_otc_list):
                    open_non_otc_list.append((k, exp_m))
    for non_otc_buy, exp_m in open_non_otc_list[:2]:
        record(
            "7. Mercado Sem OTC (Compra PRACTICE)",
            f"buy(2, '{non_otc_buy}', 'call', {exp_m}) [Sem OTC]",
            8.0,
            lambda p=non_otc_buy, e=exp_m: api.buy(2, p, "call", e),
            lambda v: (isinstance(v, tuple) and v[0] is True, f"ok={v[0]}, order_id={v[1]}"),
        )

    # Resumo Final
    ok_list = [r for r in results if r["status"] == "OK"]
    fail_list = [r for r in results if r["status"] != "OK"]
    print("\n" + "=" * 80)
    print(f"📊 RESUMO DA AUDITORIA: {len(ok_list)} FUNCIONANDO | {len(fail_list)} COM FALHA (Total: {len(results)})")
    print("=" * 80)
    if fail_list:
        print("\n❌ MÉTODOS QUE FALHARAM OU TRAVARAM:")
        for r in fail_list:
            print(f"  - [{r['category']}] {r['method']}: {r['status']} ({r['elapsed_ms']} ms) -> {r['detail']}")

    try:
        api.api.close()
    except Exception:
        pass


if __name__ == "__main__":
    main()

