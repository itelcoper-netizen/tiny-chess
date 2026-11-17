# tiny-chess-01: my own 0x88 alpha-beta engine. Fixed node budget, never a
# clock. Quiescence, TT, killers, MVV-LVA, null-move, LMR, check extensions.
# Eval: material + PSTs (king tapered mg/eg) + bishop pair. Deterministic.
import json, os, sys, urllib.error, urllib.request

P, N, B, R, Q, K = 1, 2, 3, 4, 5, 6
VAL = (0, 100, 320, 330, 500, 900, 0)
KN_OFF = (-33, -31, -18, -14, 14, 18, 31, 33)
KG_OFF = (-17, -16, -15, -1, 1, 15, 16, 17)
BI_OFF = (-17, -15, 15, 17)
RO_OFF = (-16, -1, 1, 16)
FILES = "abcdefgh"
MATE = 100000
BUDGET = 60000
PAWN = (0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0)
KNIGHT = (-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50)
BISHOP = (-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20)
ROOK = (0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0)
QUEEN = (-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20)
KING = (-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20)
EGKING = (-50,-40,-30,-20,-20,-30,-40,-50,-30,-20,-10,0,0,-10,-20,-30,-30,-10,20,30,30,20,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,20,30,30,20,-10,-30,-30,-30,0,0,0,0,-30,-30,-50,-30,-30,-30,-30,-30,-30,-50)
EGPAWN = (0,0,0,0,0,0,0,0,60,60,60,60,60,60,60,60,40,40,40,40,40,40,40,40,30,30,30,30,30,30,30,30,20,20,20,20,20,20,20,20,10,10,10,10,10,10,10,10,5,5,5,5,5,5,5,5,0,0,0,0,0,0,0,0)
EGKNIGHT = (-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,10,10,10,10,0,-10,-10,0,10,20,20,10,0,-10,-10,0,10,20,20,10,0,-10,-10,0,10,10,10,10,0,-10,-10,0,0,0,0,0,0,-10,-20,-10,-10,-10,-10,-10,-10,-20)
EGBISHOP = (-10,-10,-10,-10,-10,-10,-10,-10,-10,0,0,0,0,0,0,-10,-10,0,10,10,10,10,0,-10,-10,0,10,20,20,10,0,-10,-10,0,10,20,20,10,0,-10,-10,0,10,10,10,10,0,-10,-10,0,0,0,0,0,0,-10,-10,-10,-10,-10,-10,-10,-10,-10)
EGROOK = (5,5,5,5,5,5,5,5,20,20,20,20,20,20,20,20,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
EGQUEEN = (-10,-5,-5,-5,-5,-5,-5,-10,-5,0,0,0,0,0,0,-5,-5,0,5,5,5,5,0,-5,-5,0,5,10,10,5,0,-5,-5,0,5,10,10,5,0,-5,-5,0,5,5,5,5,0,-5,-5,0,0,0,0,0,0,-5,-10,-5,-5,-5,-5,-5,-5,-10)
PST = ((), PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING)
TAB = [[0] * 128 for _ in range(7)]
for _s in range(64):
    for _t in range(1, 6):
        TAB[_t][_s // 8 * 16 + _s % 8] = VAL[_t] + PST[_t][_s]

board = [0] * 128
side = 0
castle = 0
ep = -1
half = 0
kgs = [116, 4]
undo = []
pathc = {}
LETTER = dict(zip("PNBRQKpnbrqk", (1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14)))


def parse(fen):
    global side, castle, ep, half
    for i in range(128):
        board[i] = 0
    parts = fen.split()
    sq = 0
    for c in parts[0]:
        if c == "/":
            sq = (sq // 16 + 1) * 16
        elif c.isdigit():
            sq += int(c)
        else:
            p = LETTER[c]
            board[sq] = p
            if p == K:
                kgs[0] = sq
            elif p == K + 8:
                kgs[1] = sq
            sq += 1
    side = 0 if parts[1] == "w" else 8
    castle = 0
    if parts[2] != "-":
        if "K" in parts[2]:
            castle |= 1
        if "Q" in parts[2]:
            castle |= 2
        if "k" in parts[2]:
            castle |= 4
        if "q" in parts[2]:
            castle |= 8
    ep = -1 if parts[3] == "-" else (8 - int(parts[3][1])) * 16 + FILES.index(parts[3][0])
    half = int(parts[4]) if len(parts) > 4 else 0


def key():
    return (bytes(board), side, castle, ep)


def atk(sq, by_white):
    if by_white:
        for t in (sq + 15, sq + 17):
            if 0 <= t < 128 and not t & 0x88 and board[t] == P:
                return True
        foe = 0
    else:
        for t in (sq - 15, sq - 17):
            if 0 <= t < 128 and not t & 0x88 and board[t] == P + 8:
                return True
        foe = 8
    for off in KN_OFF:
        t = sq + off
        if not t & 0x88 and board[t] == N + foe:
            return True
    for off in KG_OFF:
        t = sq + off
        if not t & 0x88 and board[t] == K + foe:
            return True
    for off in BI_OFF:
        t = sq + off
        while not t & 0x88:
            p = board[t]
            if p:
                if p == B + foe or p == Q + foe:
                    return True
                break
            t += off
    for off in RO_OFF:
        t = sq + off
        while not t & 0x88:
            p = board[t]
            if p:
                if p == R + foe or p == Q + foe:
                    return True
                break
            t += off
    return False


def gen(caps_only=False):
    moves = []
    us = side
    for sq in range(128):
        if sq & 0x88:
            continue
        p = board[sq]
        if not p or (p & 8) != us:
            continue
        t = p & 7
        if t == P:
            d = -16 if us == 0 else 16
            start = 6 if us == 0 else 1
            last = 0 if us == 0 else 7
            one = sq + d
            if board[one] == 0:
                if one >> 4 == last:
                    for pr in (Q, R, B, N):
                        moves.append(sq | (one << 7) | (pr << 14))
                elif not caps_only:
                    moves.append(sq | (one << 7))
                    if (sq >> 4) == start:
                        two = sq + 2 * d
                        if board[two] == 0:
                            moves.append(sq | (two << 7))
            for to in (one - 1, one + 1):
                if to & 0x88:
                    continue
                q = board[to]
                if q and (q & 8) != us:
                    if to >> 4 == last:
                        for pr in (Q, R, B, N):
                            moves.append(sq | (to << 7) | (pr << 14))
                    else:
                        moves.append(sq | (to << 7))
                elif to == ep and ep != -1:
                    moves.append(sq | (to << 7))
        elif t == N or t == K:
            for off in KN_OFF if t == N else KG_OFF:
                to = sq + off
                if to & 0x88:
                    continue
                q = board[to]
                if not q or (q & 8) != us:
                    if caps_only and not q:
                        continue
                    moves.append(sq | (to << 7))
        else:
            for off in (BI_OFF if t == B else RO_OFF if t == R else BI_OFF + RO_OFF):
                to = sq + off
                while not to & 0x88:
                    q = board[to]
                    if not q:
                        if not caps_only:
                            moves.append(sq | (to << 7))
                    else:
                        if (q & 8) != us:
                            moves.append(sq | (to << 7))
                        break
                    to += off
    if not caps_only and not atk(kgs[us >> 3], us == 8):
        if us == 0:
            if castle & 1 and not board[117] and not board[118] and board[119] == R \
                    and not atk(117, False) and not atk(118, False):
                moves.append(116 | (118 << 7))
            if castle & 2 and not board[115] and not board[114] and not board[113] \
                    and board[112] == R and not atk(115, False) and not atk(114, False):
                moves.append(116 | (114 << 7))
        else:
            if castle & 4 and not board[5] and not board[6] and board[7] == R + 8 \
                    and not atk(5, True) and not atk(6, True):
                moves.append(4 | (6 << 7))
            if castle & 8 and not board[3] and not board[2] and not board[1] \
                    and board[0] == R + 8 and not atk(3, True) and not atk(2, True):
                moves.append(4 | (2 << 7))
    return moves

def make(m):
    global side, castle, ep, half
    f = m & 127
    t = (m >> 7) & 127
    pr = (m >> 14) & 7
    pc = board[f]
    cap = board[t]
    cap_sq = t
    if (pc & 7) == P and t == ep and cap == 0:
        cap_sq = t + 16 if side == 0 else t - 16
        cap = board[cap_sq]
        board[cap_sq] = 0
    undo.append((m, cap, cap_sq, castle, ep, half))
    board[t] = (pr + side) if pr else pc
    board[f] = 0
    if (pc & 7) == K:
        kgs[side >> 3] = t
        if t - f == 2:
            board[t - 1] = board[t + 1]
            board[t + 1] = 0
        elif f - t == 2:
            board[t + 1] = board[t - 2]
            board[t - 2] = 0
        castle &= ~(3 if side == 0 else 12)
    if f == 112 or t == 112:
        castle &= ~2
    if f == 119 or t == 119:
        castle &= ~1
    if f == 0 or t == 0:
        castle &= ~8
    if f == 7 or t == 7:
        castle &= ~4
    if (pc & 7) == P and abs(t - f) == 32:
        ep = (f + t) // 2
    else:
        ep = -1
    half = 0 if (pc & 7) == P or cap else half + 1
    side ^= 8


def unmake():
    global side, castle, ep, half
    m, cap, cap_sq, castle, ep, half = undo.pop()
    side ^= 8
    f = m & 127
    t = (m >> 7) & 127
    pr = (m >> 14) & 7
    pc = board[t]
    board[f] = (P + side) if pr else pc
    board[t] = 0
    if cap:
        board[cap_sq] = cap
    if (board[f] & 7) == K:
        kgs[side >> 3] = f
        if t - f == 2:
            board[t + 1] = board[t - 1]
            board[t - 1] = 0
        elif f - t == 2:
            board[t - 2] = board[t + 1]
            board[t + 1] = 0


def mnull():
    global side, ep, half
    undo.append((0, 0, 0, castle, ep, half))
    ep = -1
    half += 1
    side ^= 8


def unull():
    global side, castle, ep, half
    _, _, _, castle, ep, half = undo.pop()
    side ^= 8


def evl():
    s = 0
    wb = bb = 0
    ph = 0
    wk = bk = 0
    for sq in range(128):
        if sq & 0x88:
            continue
        p = board[sq]
        if p:
            t = p & 7
            if t == K:
                if p < 8:
                    wk = (sq >> 4) * 8 + (sq & 7)
                else:
                    bk = (7 - (sq >> 4)) * 8 + (sq & 7)
            else:
                if p < 8:
                    s += TAB[p][sq]
                    if t == B:
                        wb += 1
                else:
                    s -= TAB[p - 8][sq ^ 112]
                    if t == B:
                        bb += 1
                if t != P:
                    ph += (0, 0, 1, 1, 2, 4, 0)[t]
    if wb >= 2:
        s += 30
    if bb >= 2:
        s -= 30
    s += (KING[wk] * ph + EGKING[wk] * (24 - ph)) // 24
    s -= (KING[bk] * ph + EGKING[bk] * (24 - ph)) // 24
    return s if side == 0 else -s


nodes = 0
tt = {}
kil = [[0, 0] for _ in range(256)]


class Abort(Exception):
    pass


def order(moves, tt_move, ply):
    def sc(m):
        if m == tt_move:
            return 1 << 20
        t = (m >> 7) & 127
        v = board[t]
        if v:
            return (1 << 15) + 10 * VAL[v & 7] - (VAL[board[m & 127] & 7] >> 4)
        if ply < 256:
            if m == kil[ply][0]:
                return 1 << 14
            if m == kil[ply][1]:
                return 1 << 13
        return 0
    moves.sort(key=sc, reverse=True)
    return moves


def qs(alpha, beta, ply):
    global nodes
    nodes += 1
    if nodes > BUDGET:
        raise Abort
    if half >= 100:
        return 0
    k = key()
    if pathc.get(k):
        return 0
    stand = evl()
    if stand >= beta:
        return beta
    in_check = atk(kgs[side >> 3], side == 8)
    if not in_check and stand > alpha:
        alpha = stand
    moves = gen() if in_check else gen(caps_only=True)
    pathc[k] = 1
    a = alpha
    legal = 0
    for m in order(moves, 0, ply):
        make(m)
        if atk(kgs[(side ^ 8) >> 3], side == 0):
            unmake()
            continue
        legal += 1
        s = -qs(-beta, -a, ply + 1)
        unmake()
        if s > a:
            a = s
            if a >= beta:
                break
    del pathc[k]
    if in_check and legal == 0:
        return -MATE + ply
    return a


def search(depth, alpha, beta, ply):
    global nodes
    nodes += 1
    if nodes > BUDGET:
        raise Abort
    if half >= 100:
        return 0
    k = key()
    if pathc.get(k):
        return 0
    if depth <= 0:
        return qs(alpha, beta, ply)
    ent = tt.get(k)
    tt_move = 0
    if ent:
        if ent[0] >= depth:
            if ent[2] == 0:
                return ent[1]
            if ent[2] == 1 and ent[1] >= beta:
                return ent[1]
            if ent[2] == 2 and ent[1] <= alpha:
                return ent[1]
        tt_move = ent[3]
    in_check = atk(kgs[side >> 3], side == 8)
    pathc[k] = 1
    if in_check:
        depth += 1
    if depth >= 3 and not in_check and beta < MATE - 1000 and evl() >= beta:
        mnull()
        s = -search(depth - 3, -beta, -beta + 1, ply + 1)
        unull()
        if s >= beta:
            del pathc[k]
            return beta
    best = -MATE - 1
    best_move = 0
    a = alpha
    legal = 0
    for m in order(gen(), tt_move, ply):
        t = (m >> 7) & 127
        is_cap = board[t] != 0
        pr = (m >> 14) & 7
        make(m)
        if atk(kgs[(side ^ 8) >> 3], side == 0):
            unmake()
            continue
        legal += 1
        if legal > 3 and depth >= 3 and not is_cap and not pr and not in_check:
            s = -search(depth - 2, -a - 1, -a, ply + 1)
            if s > a:
                s = -search(depth - 1, -beta, -a, ply + 1)
        else:
            s = -search(depth - 1, -beta, -a, ply + 1)
        unmake()
        if s > best:
            best = s
            best_move = m
        if s > a:
            a = s
            if a >= beta:
                if not is_cap and ply < 256 and kil[ply][0] != m:
                    kil[ply][1] = kil[ply][0]
                    kil[ply][0] = m
                break
    del pathc[k]
    if legal == 0:
        return -MATE + ply if in_check else 0
    if best >= beta:
        fl = 1
    elif best <= alpha:
        fl = 2
    else:
        fl = 0
    if len(tt) > 400000:
        tt.clear()
    tt[k] = (depth, best, fl, best_move)
    return best

def rmoves():
    moves = []
    for m in gen():
        make(m)
        if not atk(kgs[(side ^ 8) >> 3], side == 0):
            moves.append(m)
        unmake()
    return moves


def rdep(depth, prev_best):
    moves = order(rmoves(), prev_best, 0)
    a = -MATE - 1
    best = prev_best
    best_s = -MATE - 1
    for m in moves:
        make(m)
        s = -search(depth - 1, -MATE - 1, -a, 1)
        unmake()
        if s > best_s:
            best_s = s
            best = m
        if s > a:
            a = s
    return best_s, best


def choose(fen, lu):
    global nodes
    parse(fen)
    moves = rmoves()
    if not moves:
        return lu[0]
    order(moves, 0, 0)
    best = moves[0]
    nodes = 0
    pathc.clear()
    pathc[key()] = 1
    for d in range(1, 64):
        try:
            s, m = rdep(d, best)
            best = m
            if s > MATE - 1000 or s < -MATE + 1000:
                break
        except Abort:
            break
    return uci(best)


def uci(m):
    f = m & 127
    t = (m >> 7) & 127
    s = FILES[f & 7] + str(8 - (f >> 4)) + FILES[t & 7] + str(8 - (t >> 4))
    pr = (m >> 14) & 7
    if pr:
        s += "nbrq"[pr - 2]
    return s


ENV_URL = os.environ.get("MAKEFUN_ENV_URL")


def post(path, body):
    req = urllib.request.Request(
        ENV_URL + path,
        data=json.dumps(body).encode(),
        headers={"content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"{path}: HTTP {e.code} {e.read().decode(errors='replace')}")


def main():
    if not ENV_URL:
        sys.exit("MAKEFUN_ENV_URL is not set")
    while True:
        g = post("/game", {})
        if g["status"] == "done":
            break
        while g["status"] == "your_move":
            g = post("/move", {"game": g["game"], "move": choose(g["fen"], g["legal_moves"])})
        print(f"game {g['game']}: {g['outcome']} by {g['reason']}", file=sys.stderr)
    print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost", file=sys.stderr)


if __name__ == "__main__":
    main()
