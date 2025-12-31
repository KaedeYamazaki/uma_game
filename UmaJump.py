import pyxel
import random


class Horse:
    def __init__(self):
        self.x = 50
        self.y = 100
        self.vy = 0
        self.jumping = False
        self.charging = False
        self.charge_time = 0
        self.width = 14
        self.height = 10
        self.gravity = 0.5
        self.jump_power_base = -8
        self.jump_power_max = -14
        self.max_charge_time = 20
        self.ground_y = 100

    def update(self):
        # 重力適用
        self.vy += self.gravity
        self.y += self.vy

        # 地面との衝突
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.vy = 0
            self.jumping = False

        # ジャンプチャージ（マウスクリック押し始め）
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and not self.jumping and self.y >= self.ground_y:
            self.charging = True
            self.charge_time = 0
        
        # チャージ中
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) and self.charging and not self.jumping:
            self.charge_time = min(self.charge_time + 1, self.max_charge_time)
        
        # ジャンプ実行（マウスクリック離した時）
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) and self.charging and not self.jumping:
            # チャージ時間に応じてジャンプ力を計算
            charge_ratio = self.charge_time / self.max_charge_time
            jump_power = self.jump_power_base + (self.jump_power_max - self.jump_power_base) * charge_ratio
            self.vy = jump_power
            self.jumping = True
            self.charging = False
            self.charge_time = 0
            # ジャンプ音
            pyxel.play(0, 0)

    def draw(self):
        # 体
        pyxel.rect(self.x, self.y, 14, 10, 9)
        # 頭
        pyxel.rect(self.x + 12, self.y - 6, 8, 8, 9)
        # たてがみ
        pyxel.rect(self.x + 12, self.y - 8, 6, 4, 4)
        # 脚
        pyxel.rect(self.x + 2, self.y + 10, 3, 6, 9)
        pyxel.rect(self.x + 9, self.y + 10, 3, 6, 9)
        # 目
        pyxel.rect(self.x + 16, self.y - 4, 2, 2, 0)
        
        # チャージインジケーター
        if self.charging:
            bar_width = int((self.charge_time / self.max_charge_time) * 14)
            pyxel.rect(self.x, self.y - 4, 14, 2, 0)
            pyxel.rect(self.x, self.y - 4, bar_width, 2, 10)


class Obstacle:
    def __init__(self, x, score):
        self.x = x
        self.score_value = score

        if score < 10:
            self.height = random.randint(10, 20)
        elif score < 15:
            self.height = random.randint(20, 30)
        elif score < 20:
            self.height = random.randint(20, 40)
        else:
            self.height = random.randint(30, 50)

        self.width = 12
        self.ground_y = 100

    def update(self, speed):
        self.x -= speed

    def draw(self):
        y = self.ground_y + 16  # 地面の位置に合わせる
        # 柵の柱（地面まで伸びる）
        pyxel.rect(self.x, y - self.height, 3, self.height, 4)
        pyxel.rect(self.x + 9, y - self.height, 3, self.height, 4)
        # 柵の横棒
        pyxel.rect(self.x, y - self.height, 12, 3, 4)
        if self.height > 8:  # 高さが十分にある場合のみ2本目を描画
            pyxel.rect(self.x, y - self.height + 8, 12, 3, 4)

    def is_off_screen(self):
        return self.x + self.width < 0


class Game:
    def __init__(self):
        pyxel.init(160, 144, title="午年ホースジャンプ", fps=60)
        self.setup_sounds()
        self.reset()
        pyxel.run(self.update, self.draw)

    def setup_sounds(self):
        # サウンド0: ジャンプ音
        pyxel.sounds[0].set(
            "c2e2g2",
            "t",
            "4",
            "n",
            8
        )
        
        # サウンド1: スコア音
        pyxel.sounds[1].set(
            "c3e3",
            "t",
            "3",
            "n",
            15
        )
        
        # サウンド2: ゲームオーバー音
        pyxel.sounds[2].set(
            "c2g1e1c1",
            "t",
            "5",
            "n",
            12
        )

    def reset(self):
        self.horse = Horse()
        self.obstacles = []
        self.score = 0
        self.high_score = 0
        self.game_speed = 3
        self.frame_count = 0
        self.game_state = "ready"  # ready, playing, gameover

    def update(self):
        if self.game_state == "ready":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.game_state = "playing"
                self.score = 0
                self.obstacles = []
                self.frame_count = 0
                self.game_speed = 3
                self.horse = Horse()
        
        elif self.game_state == "playing":
            self.frame_count += 1
            
            # 馬の更新
            self.horse.update()

            # 障害物の生成
            if self.frame_count % 80 == 0:
                self.obstacles.append(Obstacle(160,self.score))

            # 障害物の更新
            for obstacle in self.obstacles[:]:
                obstacle.update(self.game_speed)
                if obstacle.is_off_screen():
                    self.obstacles.remove(obstacle)
                    self.score += 1
                    # スコア音
                    pyxel.play(1, 1)

            # ゲームスピードアップ
            if self.frame_count % 300 == 0:
                self.game_speed += 1

            # 衝突判定
            if self.check_collision():
                self.game_state = "gameover"
                self.high_score = max(self.high_score, self.score)
                # ゲームオーバー音
                pyxel.play(2, 2)
        
        elif self.game_state == "gameover":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.game_state = "ready"
                self.horse = Horse()
                self.obstacles = []

    def check_collision(self):
        for obstacle in self.obstacles:
            if (obstacle.x < self.horse.x + self.horse.width and
                obstacle.x + obstacle.width > self.horse.x):
                # 地面位置を考慮した衝突判定
                if self.horse.y + self.horse.height > (self.horse.ground_y + 16) - obstacle.height:
                    return True
        return False

    def draw(self):
        # 背景（空）
        pyxel.cls(12)

        # 雲
        self.draw_clouds()

        # 地面
        pyxel.rect(0, 116, 160, 28, 3)
        
        # 草
        for i in range(0, 160, 8):
            offset = pyxel.sin(self.frame_count * 0.1 + i) * 2
            pyxel.rect(i, 114 + offset, 2, 4, 11)

        # 障害物
        for obstacle in self.obstacles:
            obstacle.draw()

        # 馬
        self.horse.draw()

        # スコア
        pyxel.text(4, 4, f"Score: {self.score}", 0)
        pyxel.text(4, 12, f"High: {self.high_score}", 0)

        # ゲーム状態表示
        if self.game_state == "ready":
            pyxel.rect(20, 45, 120, 50, 0)
            pyxel.rectb(20, 45, 120, 50, 7)
            pyxel.text(23, 55, "Hold & Release", 7)
            pyxel.text(30, 65, "to Jump High!", 7)
            pyxel.text(25, 80, "TOUCH to Start", 7)
        
        elif self.game_state == "gameover":
            pyxel.rect(20, 50, 120, 40, 0)
            pyxel.rectb(20, 50, 120, 40, 7)
            pyxel.text(45, 60, "GAME OVER!", 8)
            pyxel.text(25, 72, "TOUCH to Retry", 7)

    def draw_clouds(self):
        cloud_offset = (self.frame_count * 0.5) % 200
        
        # 雲1
        pyxel.rect(20 - cloud_offset, 20, 12, 6, 7)
        pyxel.rect(18 - cloud_offset, 22, 16, 6, 7)
        
        # 雲2
        pyxel.rect(100 - cloud_offset, 30, 10, 5, 7)
        pyxel.rect(98 - cloud_offset, 32, 14, 5, 7)


if __name__ == "__main__":
    Game()