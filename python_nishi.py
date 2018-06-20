#!/usr/bin/env python
from __future__ import print_function, division


# this is main script
# simple version

import aiwolfpy
import aiwolfpy.contentbuilder as cb

# 自分で追加
import time
import numpy as np
import pandas as pd
import random
import re
import collections

myname = 'nishi_k'

class NishiAgent(object):
    
    def __init__(self, agent_name):
        # myname
        self.myname = agent_name
        
        
    def getName(self):
        return self.myname
    
    def initialize(self, base_info, diff_data, game_setting):
        self.base_info = base_info
        # print("自分の情報")
        # print(self,base_info)
        # print("######")
        
        # game_setting
        self.game_setting = game_setting

        # COしたか
        self.co = False

        # 生きている人数
        self.alive = self.game_setting['playerNum']

        # 各ユーザの疑い予測値
        if self.game_setting['playerNum'] == 5:
            # 村人陣営か
            self.villager_g = (self.base_info['myRole'] == 'VILLAGER' or self.base_info['myRole'] == 'SEER' or self.base_info['myRole'] == 'MEDIUM')
            #役持ち村人か
            self.role_villager = (self.base_info['myRole'] == 'SEER' or self.base_info['myRole'] == 'MEDIUM')
            #人狼陣営か
            self.wolf_g = (self.base_info['myRole'] == 'POSSESSED' or self.base_info['myRole'] == 'WEREWOLF')

            # COした人を覚えておく
            self.comingout = {'VILLAGER': [], 'POSSESSED': [], 'SEER': [], 'WEREWOLF': [], 'MEDIUM': []} 
            # 怪しさ(0は白(主観),-1は死亡(事実))
            self.suspicious = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1}
            # 自分は怪しくない
            self.suspicious[self.base_info['agentIdx']] = -10
            
            # 投票された回数(初期は勿論0)
            self.voted = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

            #占い結果(占い師の時)
            self.divined = {1: 'UNKNOWN', 2: 'UNKNOWN', 3: 'UNKNOWN', 4: 'UNKNOWN', 5: 'UNKNOWN'}
            # 自分は既知
            self.divined[self.base_info['agentIdx']] = self.base_info['myRole']
            # 占い結果を伝える時に使用
            self.seer_flag = False
            self.seer_divined_id = self.base_info['agentIdx']
            self.seer_divined_role = 'UNKNOWN'

        else:
            # 村人陣営か
            self.villager_g = (self.base_info['myRole'] == 'VILLAGER' or self.base_info['myRole'] == 'BODYGUARD' or self.base_info['myRole'] == 'SEER' or self.base_info['myRole'] == 'MEDIUM')
            #役持ち村人か
            self.role_villager = (self.base_info['myRole'] == 'SEER' or self.base_info['myRole'] == 'MEDIUM')
            #人狼陣営か
            self.wolf_g = (self.base_info['myRole'] == 'POSSESSED' or self.base_info['myRole'] == 'WEREWOLF')

            # COした人を覚えておく
            self.comingout = {'VILLAGER': [], 'BODYGUARD': [], 'POSSESSED': [], 'SEER': [], 'MEDIUM': [], 'WEREWOLF': []}
            # 怪しさ(0は白(主観),-1は死亡(事実))
            self.suspicious = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1}
            # 自分は怪しくない
            self.suspicious[self.base_info['agentIdx']] = -10

            # 投票された回数(初期は勿論0)
            self.voted = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0}

            #占い結果(占い師の時)
            self.divined = {1: 'UNKNOWN', 2: 'UNKNOWN', 3: 'UNKNOWN', 4: 'UNKNOWN', 5: 'UNKNOWN', 6: 'UNKNOWN', 7: 'UNKNOWN', 8: 'UNKNOWN', 9: 'UNKNOWN', 10: 'UNKNOWN', 11: 'UNKNOWN', 12: 'UNKNOWN', 13: 'UNKNOWN', 14: 'UNKNOWN', 15: 'UNKNOWN'}
            # 自分は既知
            self.divined[self.base_info['agentIdx']] = self.base_info['myRole']
            # 占い結果を伝える時に使用
            self.seer_flag = False
            self.seer_divined_id = self.base_info['agentIdx']
            self.seer_divined_role = 'UNKNOWN'

    def update(self, base_info, diff_data, request):
        # print(base_info)
        # print(diff_data)
        self.base_info = base_info

        # SEER,MEDIUMのCOは怪しむ
        for (i,j,k) in zip(diff_data['text'],diff_data['agent'],diff_data['type']):
            tWords = i.split(' ')

            # COに対する反応
            if (tWords[0] == 'COMINGOUT'):
                tAgent_idx = int(re.split('[\[,\]]', tWords[1])[1])
                # 自分のCOは無視
                if tAgent_idx != self.base_info['agentIdx']:
                    # print(tWords)

                    # comingoutメモ
                    if tWords[2] in self.comingout.keys():
                        self.comingout[tWords[2]].append(tAgent_idx)
                    else:
                        print("エラー：append時")
                        print("----------------------------------")

                    # 自分の役職と同じ時超怪しい
                    if tWords[2] == self.base_info['myRole']:
                        if tWords[2] == 'MEDIUM' or tWords[2] == 'SEER' or tWords[2] == 'POSSESSED' or tWords[2] == 'BODYGUARD':
                            self.suspicious[tAgent_idx] += 100
                            # print("怪しさ更新：Agent[" + str(tAgent_idx) + "]が超黒っぽい")
                            # print(self.suspicious)
                            # print("----------------------------------")
                            
                    if tWords[2] == 'SEER' or tWords[2] == 'MEDIUM':
                        # 複数人の場合は全員怪しむ
                        # 現状          (coming outが起こるたびに怪しさ上がる)
                        if len(self.comingout[tWords[2]]) >= 2:
                            for i in self.comingout[tWords[2]]:
                                # 自分の怪しさは増えない，評価マイナスの人も増えない
                                if i != self.base_info['agentIdx'] and self.suspicious[i] >= 0:
                                    self.suspicious[i] += 1
                                    # print("怪しさ更新：複数立候補")
                                    # print(self.suspicious)
                                    # print("----------------------------------")
                                    
            # 占い結果に対する反応(方針：全面定期に信用するが信用度によって重み付けする) 
            # 死んでいる人は占わないと仮定
            if (tWords[0] == 'DIVINED'):
                tAgent_idx = int(re.split('[\[,\]]', tWords[1])[1])
                #占い結果
                tSpecies = tWords[2]
                # 生きているCO占い師の数と，idxリストと怪しさリスト
                tNum_seer, tAlive_seer_idx, tAlive_seer_sus_val = self.__alive_co_xxx('SEER')
                # CO占い師が一人しかいない場合は全面的に信用(COがいない場合もこちら)
                if (tSpecies == 'HUMAN' and tNum_seer <= 1):
                    self.suspicious[tAgent_idx] = 0
                else:
                    #一人以上の時は重み付けて減らす seer/sum suspicious of all co_seer
                    tDenominator = sum(tAlive_seer_sus_val)
                    tNumerator = self.suspicious[int(j)]
                    if tDenominator == 0 and len(tAlive_seer_sus_val) != 0:
                        tDenominator = len(tAlive_seer_sus_val)
                        tNumerator = 1
                    else:
                        tDenominator = 1
                        tNumerator = 1
                    self.suspicious[tAgent_idx] *= (tNumerator / tDenominator)
                    
                
                # print("怪しさ更新：占い")
                # print(self.suspicious)
                # print("----------------------------------")
            
            if k == 'vote':
                tAgent_idx = int(re.split('[\[,\]]', tWords[1])[1])
                # 投票された人をカウント
                self.voted[tAgent_idx] += 1

            # 自分が占い師の時の占い結果
            if k == 'divine':
                tAgent_idx = int(re.split('[\[,\]]', tWords[1])[1])
                if tWords[2] == 'HUMAN' or tWords[2] == 'WEREWOLF':
                    self.divined[tAgent_idx] = tWords[2]
                    self.seer_flag = True
                    self.seer_divined_id = tAgent_idx
                    self.seer_divined_role = tWords[2]
                    # print("占い結果更新")
                    # print(self.divined)
                    # print("----------------------------------")



        
    def dayStart(self):
        #生きている人数計算
        self.alive = self.__num_alive()

        # 死んだ人は-1にしてみる
        for key, value in self.base_info['statusMap'].items():
            if value == "DEAD":
                # print(str(key) + " is DEAD")
                self.suspicious[int(key)] = -1
                # print("怪しさ更新：死者増加")
                # print(self.suspicious)
                # print("----------------------------------")

        # 投票結果を考慮し怪しさ更新
        tCount, tAlive_idx, tAlive_voted_num = self.__voted_info()
        tAll_voted_num = sum(tAlive_voted_num)

        if tAll_voted_num > 0:
            for i in tAlive_idx:
                self.suspicious[i] *= (1 + self.voted[i] / tAll_voted_num)
                
            # print("怪しさ更新：被投票数")
            # print(self.suspicious)
            # print("----------------------------------")
        
        self.talk_turn = 0
        self.whisper_turn = 0
        return None
    
    def talk(self):
        # 時間計測
        start = time.time()
        self.talk_turn += 1
        #乱数
        tSkip_num = random.randint(1, 10)

        # 1日目(SEER or POSSESSEDならCOしみてる)
        if self.base_info['day'] == 1 and self.talk_turn == 1 and not(self.co):
            if self.base_info['myRole'] == 'SEER' or self.base_info['myRole'] == 'POSSESSED':
                if time.time()-start >= 0.1:
                    print("over talk time")
                # print("SEERでカミングアウトして見た :" + self.base_info['myRole'])
                self.co = True
                return cb.comingout(self.base_info['agentIdx'], 'SEER')

        # 役持ち村人の時，偽物がCOしてたら自分も名乗り出る
        if not(self.co) and self.role_villager and len(self.comingout[self.base_info['myRole']]) >= 1:
            # print("偽物が名乗り出たのでCOしました")
            self.co = True
            return cb.comingout(self.base_info['agentIdx'], self.base_info['myRole'])
            
        
        # 数ターン様子を見てみる
        if self.talk_turn < tSkip_num:
            if time.time()-start >= 0.1:
                print("over talk time")
            return cb.skip()

        # 占い結果が出た時に伝える(skipを何回かしてみる)
        if self.base_info['myRole'] == 'SEER' and self.seer_flag:
            self.seer_flag = False
            # print("占い結果報告")
            # print('Agent' + str(self.seer_divined_id) + 'が' + self.seer_divined_role)
            # print("----------------------------------")
            return cb.divined(self.seer_divined_id,self.seer_divined_role)
        
        if time.time()-start >= 0.1:
            print("over talk time")
        return cb.over()
    
    def whisper(self):
        self.whisper_turn += 1
        # whisperの最初の会話で食べる人宣言
        if self.whisper_turn == 1:
            # 最も人間らしい人を食べると宣言
            return str(self.__n_th_suspicious(self.alive-1))
        return cb.over()
        
    def vote(self):
        # 村人陣営の時
        if self.villager_g:
            #霊媒師が2人以上いる場合は優先
            tCount_med, tAlive_med_idx, tAlive_med_sus_val = self.__alive_co_xxx('MEDIUM')

            # 一番怪しい，生きてるCO霊媒師を選ぶ
            if tCount_med >= 2:
                # print("ローラー")
                # print(self.comingout)
                # print(self.suspicious)
                # print("vote:" + str(tAlive_med_idx[tAlive_med_sus_val.index(max(tAlive_med_sus_val))]))
                # print("------------------------------")
                return tAlive_med_idx[tAlive_med_sus_val.index(max(tAlive_med_sus_val))]
                
            # 一番疑っている人を選択
            tVote_idx = max([(v, k) for k, v in self.suspicious.items()])[1]
        else:
            # 人狼陣営の時(2番目に怪しいと思っている人を選ぶ)
            tVote_idx = self.__n_th_suspicious(2)

        # print("投票時の怪しさ")
        # print(self.suspicious)
        # print("vote:" + str(tVote_idx))
        # print("------------------------------")
        return tVote_idx
    
    def attack(self):
        # 一番人間らしい人を食べる
        return str(self.__n_th_suspicious(self.alive-1))
    
    def divine(self):
        # 推測の中でもっとも疑わしいものを占う
        tIdx = int(list(self.base_info['remainTalkMap'].keys())[0])
        for i in range(self.alive):
            tIdx = self.__n_th_suspicious(i + 1)
            if self.suspicious[tIdx] < 10:
                break
        return str(tIdx)
    
    def guard(self):
        # 占い師最優先，最も怪しくない人を守る
        tCount, tAlive_idx, tAlive_sus_val = self.__alive_co_xxx('SEER')
        if tCount > 0:
            tKeys = np.array(tAlive_idx)
            tVals = np.array(tAlive_sus_val)
            return tKeys[tVals.argsort()[0]]
        
        if self.game_setting['playerNum'] == 15:
            tCount, tAlive_idx, tAlive_sus_val = self.__alive_co_xxx('MEDIUM')
            if tCount > 0:
                tKeys = np.array(tAlive_idx)
                tVals = np.array(tAlive_sus_val)
                return tKeys[tVals.argsort()[0]]
            
        # 生きてる中で最も怪しくない人を守る
        return self.__n_th_suspicious(self.alive)
    
    def finish(self):
        return None

    # 生きているCO_XXXの数と，idxリスト，怪しさリストを返す
    def __alive_co_xxx(self, aName):
        tIdx = self.comingout[aName]
        tCount = 0
        tAlive_idx = []
        tAlive_sus_val = []
        # 生きているCO霊媒師の数を数える
        for i in tIdx:
            if self.base_info['statusMap'][str(i)] == 'ALIVE':
                tAlive_idx.append(i)
                tAlive_sus_val.append(self.suspicious[i])
                tCount += 1
        return tCount, tAlive_idx, tAlive_sus_val

    # 生きているプレイヤー数と，idxリスト，被投票数リストを返す
    def __voted_info(self):
        tIdx = list(self.voted.keys())
        tCount = 0
        tAlive_idx = []
        tAlive_voted_num = []
        # 生きているCO霊媒師の数を数える
        for i in tIdx:
            if self.base_info['statusMap'][str(i)] == 'ALIVE':
                tAlive_idx.append(i)
                tAlive_voted_num.append(self.voted[i])
                tCount += 1
        return tCount, tAlive_idx, tAlive_voted_num

    # n番目に怪しい人のidx
    def __n_th_suspicious(self, aN):
        tKeys = np.array(list(self.suspicious.keys()))
        tVals = np.array(list(self.suspicious.values()))
        return tKeys[tVals.argsort()[::-1][aN - 1]]
        
    #生きている人数
    def __num_alive(self):
        return list(self.base_info['statusMap'].values()).count('ALIVE')
        
        

    
agent = NishiAgent(myname)

# run
if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
    