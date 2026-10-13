# 新证据标注迁移复核草稿

全部条目等待人工复核，禁止直接用于正式评分。
引文命中仅用于生成候选，不自动证明完整答案或人物/事件条件被支持。

| ID | 可回答 | 状态 | 新证据候选/负例故事块 |
|---|---|---|---|
| q001 | True | quote_candidates_require_semantic_review | story_000000_chunk_000 |
| q002 | True | quote_candidates_require_semantic_review | story_000130_chunk_000, story_000130_chunk_001 |
| q003 | True | quote_candidates_require_semantic_review | story_000256_chunk_000, story_000256_chunk_001 |
| q004 | True | quote_candidates_require_semantic_review | story_000379_chunk_000 |
| q005 | True | quote_candidates_require_semantic_review | story_000515_chunk_000 |
| q006 | True | quote_candidates_require_semantic_review | story_000656_chunk_000 |
| q007 | True | quote_candidates_require_semantic_review | story_000741_chunk_003 |
| q008 | True | quote_candidates_require_semantic_review | story_000806_chunk_001 |
| q009 | True | quote_candidates_require_semantic_review | story_000921_chunk_001 |
| q010 | True | quote_candidates_require_semantic_review | story_000978_chunk_001, story_000978_chunk_002 |
| q011 | True | quote_candidates_require_semantic_review | story_001097_chunk_000 |
| q012 | True | quote_candidates_require_semantic_review | story_001240_chunk_000 |
| q013 | True | quote_candidates_require_semantic_review | story_001385_chunk_000, story_001385_chunk_001 |
| q014 | True | quote_candidates_require_semantic_review | story_001529_chunk_000, story_001529_chunk_001 |
| q015 | True | quote_candidates_require_semantic_review | story_001662_chunk_000 |
| q016 | True | quote_candidates_require_semantic_review | story_001795_chunk_001 |
| q017 | True | quote_candidates_require_semantic_review | story_001920_chunk_000, story_001920_chunk_001 |
| q018 | True | quote_candidates_require_semantic_review | story_002045_chunk_001 |
| q019 | True | quote_candidates_require_semantic_review | story_002137_chunk_007, story_002137_chunk_008 |
| q020 | True | quote_candidates_require_semantic_review | story_002205_chunk_000 |
| q021 | True | quote_candidates_require_semantic_review | story_002292_chunk_001 |
| q022 | True | quote_candidates_require_semantic_review | story_002365_chunk_001 |
| q023 | True | quote_candidates_require_semantic_review | story_002511_chunk_000 |
| q024 | True | quote_candidates_require_semantic_review | story_002640_chunk_001, story_002640_chunk_002 |
| q025 | True | quote_candidates_require_semantic_review | story_002763_chunk_000 |
| q026 | True | quote_candidates_require_semantic_review | story_002893_chunk_001 |
| q027 | True | quote_candidates_require_semantic_review | story_003037_chunk_000 |
| q028 | True | quote_candidates_require_semantic_review | story_003178_chunk_000, story_003178_chunk_001 |
| q029 | True | quote_candidates_require_semantic_review | story_003318_chunk_000 |
| q030 | True | quote_candidates_require_semantic_review | story_003461_chunk_000 |
| q031 | True | quote_candidates_require_semantic_review | story_003600_chunk_000 |
| q032 | True | quote_candidates_require_semantic_review | story_003730_chunk_000, story_003730_chunk_001 |
| q033 | True | quote_candidates_require_semantic_review | story_003851_chunk_000 |
| q034 | True | quote_candidates_require_semantic_review | story_003975_chunk_000 |
| q035 | True | quote_candidates_require_semantic_review | story_004119_chunk_001 |
| q036 | True | quote_candidates_require_semantic_review | story_004256_chunk_000 |
| q037 | True | quote_candidates_require_semantic_review | story_004378_chunk_001 |
| q038 | True | quote_candidates_require_semantic_review | story_004500_chunk_000, story_004500_chunk_001 |
| q039 | True | quote_candidates_require_semantic_review | story_004638_chunk_000, story_004638_chunk_001 |
| q040 | True | quote_candidates_require_semantic_review | story_004763_chunk_000 |
| q041 | False | story_scope_requires_absence_review | story_000000_chunk_000, story_000000_chunk_001 |
| q042 | False | story_scope_requires_absence_review | story_004500_chunk_000, story_004500_chunk_001 |
| q043 | False | story_scope_requires_absence_review | story_001662_chunk_000, story_001662_chunk_001 |
| q044 | False | story_scope_requires_absence_review | story_002365_chunk_000, story_002365_chunk_001 |
| q045 | False | story_scope_requires_absence_review | story_001097_chunk_000, story_001097_chunk_001 |

## q001

问题：Who found a needle in her room and wanted her mother to sew a button on her shirt?

预期答案：Lily

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
One day, a little girl named Lily found a needle in her room. She knew it was difficult to play with it because it was sharp. Lily wanted to share the needle with her mom, so she could sew a button on her shirt.

Lily went to her mom and said, "Mom, I found this needle. Can you share it with me and sew my shirt?" Her mom smiled and said, "Yes, Lily, we can share the needle and fix your shirt."

Together, they shared the needle and sewed the button on Lily's shirt. It was not difficult for them because they were sharing and helping each other. After they finished, Lily thanked her mom for sharing the needle and fixing her shirt. They both felt happy because they had shared and worked together.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_000000_chunk_000**

```text
One day, a little girl named Lily found a needle in her room. She knew it was difficult to play with it because it was sharp. Lily wanted to share the needle with her mom, so she could sew a button on her shirt.

Lily went to her mom and said, "Mom, I found this needle. Can you share it with me and sew my shirt?" Her mom smiled and said, "Yes, Lily, we can share the needle and fix your shirt."

Together, they shared the needle and sewed the button on Lily's shirt. It was not difficult for them because they were sharing and helping each other
```

**story_000000_chunk_001**

```text
 shirt."

Together, they shared the needle and sewed the button on Lily's shirt. It was not difficult for them because they were sharing and helping each other. After they finished, Lily thanked her mom for sharing the needle and fixing her shirt. They both felt happy because they had shared and worked together.
```


## q002

问题：Which animal chased the little mouse, barked loudly, and caught up with it?

预期答案：A big dog

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time there was a bridge. It was very smooth. All the animals wanted to walk on top of it.

One day a little mouse was walking across the bridge. He saw a big dog on the other side and the little mouse wanted to show the dog how brave he was. He bowed to the big dog and kept walking.

The big dog didn't like the little mouse and he chased him to the other side. The little mouse was so scared and screamed for help. Unfortunately no-one was around to help him.

The big dog finally caught up with the little mouse and he was so angry. He barked very loudly and the little mouse screamed and ran away as fast as he could.

But it was too late. The big dog had been too fast and the little mouse was never seen again.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_000130_chunk_000**

```text
Once upon a time there was a bridge. It was very smooth. All the animals wanted to walk on top of it.

One day a little mouse was walking across the bridge. He saw a big dog on the other side and the little mouse wanted to show the dog how brave he was. He bowed to the big dog and kept walking.

The big dog didn't like the little mouse and he chased him to the other side. The little mouse was so scared and screamed for help. Unfortunately no-one was around to help him.

The big dog finally caught up with the little mouse and he was so angry. He barked very loudly
```

**story_000130_chunk_001**

```text
 help. Unfortunately no-one was around to help him.

The big dog finally caught up with the little mouse and he was so angry. He barked very loudly and the little mouse screamed and ran away as fast as he could.

But it was too late. The big dog had been too fast and the little mouse was never seen again.
```


## q003

问题：Why was Tim sad when Jack was going away to university?

预期答案：He was sad that they would be separated.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time there were two best friends named Tim and Jack. They had been friends since they were little and always looked out for each other.

One day, Jack got the exciting news that he had been accepted to the university of his dreams. He was so excited to get started on this new adventure. He told Tim the good news with glee, but Tim didn't seem as excited.

"Why aren't you happy for me?" asked Jack.

Tim sighed and replied, "I'm happy for you, but I'm also sad. We will be separated now that you're going away. I don't want that to happen!"

Jack smiled and said, "That's okay, we will stay in touch and be best friends forever. Just because I'm going to the university, doesn't mean you and I can't still have a chat when we are feeling a bit messy." 

Tim smiled, happy to know that his best friend would still be around even if they were separated. They gave each other a hug and promised to keep in touch. 

The moral of the story is that even when apart, you can still stay close to your friends if you remember to stay connected.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_000256_chunk_000**

```text
Once upon a time there were two best friends named Tim and Jack. They had been friends since they were little and always looked out for each other.

One day, Jack got the exciting news that he had been accepted to the university of his dreams. He was so excited to get started on this new adventure. He told Tim the good news with glee, but Tim didn't seem as excited.

"Why aren't you happy for me?" asked Jack.

Tim sighed and replied, "I'm happy for you, but I'm also sad. We will be separated now that you're going away. I don't want that to happen!"


```

**story_000256_chunk_001**

```text
 "I'm happy for you, but I'm also sad. We will be separated now that you're going away. I don't want that to happen!"

Jack smiled and said, "That's okay, we will stay in touch and be best friends forever. Just because I'm going to the university, doesn't mean you and I can't still have a chat when we are feeling a bit messy." 

Tim smiled, happy to know that his best friend would still be around even if they were separated. They gave each other a hug and promised to keep in touch. 

The moral of the story is that even when apart,
```

**story_000256_chunk_002**

```text
 around even if they were separated. They gave each other a hug and promised to keep in touch. 

The moral of the story is that even when apart, you can still stay close to your friends if you remember to stay connected.
```


## q004

问题：Why did Sally hesitate before trying to go up the pale stair?

预期答案：It was too high and too far.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
The pale stair was long. Sally wanted to go up it. But she had to delay. It was too high and too far.

Instead she waited and waited. She watched her mommy go up it. Mommy said she'd wait for Sally at the top. Sally wanted to see what was up there.

Finally, Sally decided she'd try the big pale stair. One slow step at a time, she followed her mommy. It was a long way up the stair!

Soon Sally reached the top. She was very proud of herself. She could see everything from up here. Mommy smiled at her. She said, "I am proud of you, Sally."
```

### 全部目标故事文段（候选外的文段也需检查）

**story_000379_chunk_000**

```text
The pale stair was long. Sally wanted to go up it. But she had to delay. It was too high and too far.

Instead she waited and waited. She watched her mommy go up it. Mommy said she'd wait for Sally at the top. Sally wanted to see what was up there.

Finally, Sally decided she'd try the big pale stair. One slow step at a time, she followed her mommy. It was a long way up the stair!

Soon Sally reached the top. She was very proud of herself. She could see everything from up here. Mommy smiled at her. She said, "I am
```

**story_000379_chunk_001**

```text
 Sally reached the top. She was very proud of herself. She could see everything from up here. Mommy smiled at her. She said, "I am proud of you, Sally."
```


## q005

问题：What did Lucy receive from her mother in exchange for helping clean the house?

预期答案：A white hut to play with.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once there was a little girl. Her name was Lucy. She wanted something new to play with so she asked her Mom. Her Mom said, "I have an offer for you!" Lucy was very excited. Her Mom said, "If you help me clean the house, I'll give you a white hut to play with." So Lucy cleaned the house and sure enough, her Mom had a white hut waiting for her when she was done. 

Lucy was very happy. She dragged the hut into the backyard and played in it all day. She used it as a magical castle and pretended she was a princess. She called it her secret hideaway. Every day, she would go outside and play in her white hut. 

She thanked her Mom for the hut, and Mom said, "You're welcome. It's nice to offer you something special to play with." Lucy smiled and hugged her Mom. They were both very happy.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_000515_chunk_000**

```text
Once there was a little girl. Her name was Lucy. She wanted something new to play with so she asked her Mom. Her Mom said, "I have an offer for you!" Lucy was very excited. Her Mom said, "If you help me clean the house, I'll give you a white hut to play with." So Lucy cleaned the house and sure enough, her Mom had a white hut waiting for her when she was done. 

Lucy was very happy. She dragged the hut into the backyard and played in it all day. She used it as a magical castle and pretended she was a princess. She called it her
```

**story_000515_chunk_001**

```text
 She dragged the hut into the backyard and played in it all day. She used it as a magical castle and pretended she was a princess. She called it her secret hideaway. Every day, she would go outside and play in her white hut. 

She thanked her Mom for the hut, and Mom said, "You're welcome. It's nice to offer you something special to play with." Lucy smiled and hugged her Mom. They were both very happy.
```


## q006

问题：What pictures decorated the special card Lily made for her mother, alongside the words I love you?

预期答案：Hearts and flowers.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a girl named Lily. She loved to draw pictures for her family and friends. One day, Lily made a special card for her mom. It had hearts and flowers on it, and said "I love you" in big letters.

When Lily gave the card to her mom, she was very polite and said "thank you, sweetie". Lily felt happy because her mom liked the card. She loved making her mom happy.

From that day on, Lily made cards for everyone she loved. She would draw pictures and write nice words on them. And everyone was always polite and said thank you. Lily was happy because she loved making people feel happy with her cards.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_000656_chunk_000**

```text
Once upon a time, there was a girl named Lily. She loved to draw pictures for her family and friends. One day, Lily made a special card for her mom. It had hearts and flowers on it, and said "I love you" in big letters.

When Lily gave the card to her mom, she was very polite and said "thank you, sweetie". Lily felt happy because her mom liked the card. She loved making her mom happy.

From that day on, Lily made cards for everyone she loved. She would draw pictures and write nice words on them. And everyone was always polite and said thank you. Lily
```

**story_000656_chunk_001**

```text
 on, Lily made cards for everyone she loved. She would draw pictures and write nice words on them. And everyone was always polite and said thank you. Lily was happy because she loved making people feel happy with her cards.
```


## q007

问题：Who slid down together and hugged after Max ran away from the slide?

预期答案：Ben and Lily.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Ben and Lily were friends who liked to play together. They had different skin colors: Ben's skin was brown and Lily's skin was white. They did not care about that. They cared about having fun.

One day, they went to the park with their moms. They saw a big slide and ran to it. Ben went first and slid down fast. He laughed and said, "That was fun! Come on, Lily!"

Lily climbed up the ladder and got ready to slide. But then she saw a boy with red hair and green eyes. He was waiting for his turn. He looked at Lily and said, "Hey, you have weird skin. What is your name?"

Lily felt sad and scared. She did not like the boy's words. She said, "My name is Lily. What is your name?"

The boy said, "My name is Max. And I have the best skin. It is red and green, like a firework. You have boring skin. It is white, like snow. I am envious of nothing."

Ben heard what Max said. He felt angry and brave. He climbed up the ladder and stood next to Lily. He said, "You are wrong, Max. Lily's skin is not boring. It is beautiful, like a flower. And my skin is not weird. It is cool, like chocolate. We have different skin, but we are both good. You are envious of everything."

Max did not know what to say. He felt ashamed and small. He ran away from the slide. Ben and Lily smiled at each other. They slid down together and hugged. They were happy and proud. Their moms saw them and clapped. They had the best skin. It was the skin of friends.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_000741_chunk_000**

```text
Ben and Lily were friends who liked to play together. They had different skin colors: Ben's skin was brown and Lily's skin was white. They did not care about that. They cared about having fun.

One day, they went to the park with their moms. They saw a big slide and ran to it. Ben went first and slid down fast. He laughed and said, "That was fun! Come on, Lily!"

Lily climbed up the ladder and got ready to slide. But then she saw a boy with red hair and green eyes. He was waiting for his turn. He looked at Lily and said, "Hey
```

**story_000741_chunk_001**

```text
 to slide. But then she saw a boy with red hair and green eyes. He was waiting for his turn. He looked at Lily and said, "Hey, you have weird skin. What is your name?"

Lily felt sad and scared. She did not like the boy's words. She said, "My name is Lily. What is your name?"

The boy said, "My name is Max. And I have the best skin. It is red and green, like a firework. You have boring skin. It is white, like snow. I am envious of nothing."

Ben heard what Max said. He felt
```

**story_000741_chunk_002**

```text
 like a firework. You have boring skin. It is white, like snow. I am envious of nothing."

Ben heard what Max said. He felt angry and brave. He climbed up the ladder and stood next to Lily. He said, "You are wrong, Max. Lily's skin is not boring. It is beautiful, like a flower. And my skin is not weird. It is cool, like chocolate. We have different skin, but we are both good. You are envious of everything."

Max did not know what to say. He felt ashamed and small. He ran away from the slide. Ben and Lily
```

**story_000741_chunk_003**

```text
. You are envious of everything."

Max did not know what to say. He felt ashamed and small. He ran away from the slide. Ben and Lily smiled at each other. They slid down together and hugged. They were happy and proud. Their moms saw them and clapped. They had the best skin. It was the skin of friends.
```


## q008

问题：Why did Timmy feel embarrassed when he joined the older kids' game at the fair?

预期答案：He did not know the rules, made a mistake, and the kids laughed and teased him.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a little boy named Timmy. Timmy loved to play outside and watch the birds fly in the sky. One day, Timmy's mom told him they were going to a fair. Timmy was so excited!

At the fair, Timmy saw a big ride with swings that went up high in the air. Timmy wanted to go on it so badly, but he was too short. Timmy's mom said they could come back when he was taller.

Later, Timmy saw a group of older kids playing a game. They asked Timmy if he wanted to play too. Timmy was happy to join, but he didn't know the rules. When he made a mistake, the older kids laughed and teased him. Timmy felt embarrassed.

As they were leaving the fair, Timmy saw a butterfly. It reminded him of the birds he loved to watch. He knew he would grow taller one day and be able to ride the swings. And he also knew that it's okay to make mistakes and feel embarrassed sometimes.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_000806_chunk_000**

```text
Once upon a time, there was a little boy named Timmy. Timmy loved to play outside and watch the birds fly in the sky. One day, Timmy's mom told him they were going to a fair. Timmy was so excited!

At the fair, Timmy saw a big ride with swings that went up high in the air. Timmy wanted to go on it so badly, but he was too short. Timmy's mom said they could come back when he was taller.

Later, Timmy saw a group of older kids playing a game. They asked Timmy if he wanted to play too. Timmy
```

**story_000806_chunk_001**

```text
 when he was taller.

Later, Timmy saw a group of older kids playing a game. They asked Timmy if he wanted to play too. Timmy was happy to join, but he didn't know the rules. When he made a mistake, the older kids laughed and teased him. Timmy felt embarrassed.

As they were leaving the fair, Timmy saw a butterfly. It reminded him of the birds he loved to watch. He knew he would grow taller one day and be able to ride the swings. And he also knew that it's okay to make mistakes and feel embarrassed sometimes.
```


## q009

问题：What tool did Ben try to put into the box lock after seeing it on the table where Mom had cut dough?

预期答案：A dull knife.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Lila and Ben were bored. They had no toys to play with. All their toys were in a big box. But the box had a lock. And they did not have the key.

"Where is the key?" Lila asked.

"I don't know," Ben said. "Maybe Mom has it."

They looked for Mom. But Mom was busy. She was making dough. She was going to bake a cake.

"Mom, can we have the key?" Lila asked.

"Not now, sweetie," Mom said. "I'm busy. Go play with something else."

But there was nothing else to play with. Lila and Ben were sad. They went back to the box. They tried to open it. But it was too hard.

"Maybe we can use something to unlock it," Ben said.

"Like what?" Lila asked.

Ben looked around. He saw a dull knife. It was on the table. Mom had used it to cut the dough.

"Maybe this will work," Ben said. He took the knife. He went to the box. He tried to put the knife in the lock. But it did not fit.

"Be careful, Ben," Lila said. "You might hurt yourself."

Ben did not listen. He pushed harder. He twisted the knife. He heard a click. He smiled.

"I did it!" he said. "I unlocked the box!"

He opened the box. He saw all their toys. He was happy. He took out his favorite car. He gave Lila her favorite doll.

"Look, Lila," he said. "We can play now!"

Lila was happy too. She hugged her doll. She thanked Ben.

"You're smart, Ben," she said. "You unlocked the box!"

They played with their toys. They had fun. They forgot about Mom and the dough. They did not hear Mom calling them.

"Kids, come here!" Mom said. "The cake is ready!"

But Lila and Ben did not hear. They were too busy playing. They were not bored anymore. They were happy.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_000921_chunk_000**

```text
Lila and Ben were bored. They had no toys to play with. All their toys were in a big box. But the box had a lock. And they did not have the key.

"Where is the key?" Lila asked.

"I don't know," Ben said. "Maybe Mom has it."

They looked for Mom. But Mom was busy. She was making dough. She was going to bake a cake.

"Mom, can we have the key?" Lila asked.

"Not now, sweetie," Mom said. "I'm busy. Go play with something else."

But there was nothing else to play with.
```

**story_000921_chunk_001**

```text
ila asked.

"Not now, sweetie," Mom said. "I'm busy. Go play with something else."

But there was nothing else to play with. Lila and Ben were sad. They went back to the box. They tried to open it. But it was too hard.

"Maybe we can use something to unlock it," Ben said.

"Like what?" Lila asked.

Ben looked around. He saw a dull knife. It was on the table. Mom had used it to cut the dough.

"Maybe this will work," Ben said. He took the knife. He went to the box. He tried to put
```

**story_000921_chunk_002**

```text
 had used it to cut the dough.

"Maybe this will work," Ben said. He took the knife. He went to the box. He tried to put the knife in the lock. But it did not fit.

"Be careful, Ben," Lila said. "You might hurt yourself."

Ben did not listen. He pushed harder. He twisted the knife. He heard a click. He smiled.

"I did it!" he said. "I unlocked the box!"

He opened the box. He saw all their toys. He was happy. He took out his favorite car. He gave Lila her favorite doll.

"Look,
```

**story_000921_chunk_003**

```text
 opened the box. He saw all their toys. He was happy. He took out his favorite car. He gave Lila her favorite doll.

"Look, Lila," he said. "We can play now!"

Lila was happy too. She hugged her doll. She thanked Ben.

"You're smart, Ben," she said. "You unlocked the box!"

They played with their toys. They had fun. They forgot about Mom and the dough. They did not hear Mom calling them.

"Kids, come here!" Mom said. "The cake is ready!"

But Lila and Ben did not hear. They were too busy
```

**story_000921_chunk_004**

```text
 Mom calling them.

"Kids, come here!" Mom said. "The cake is ready!"

But Lila and Ben did not hear. They were too busy playing. They were not bored anymore. They were happy.
```


## q010

问题：Why did Mom say Ben and Lily could not swim with the ducks they had shared olives with?

预期答案：The pond was too deep and cold, and the ducks needed their space.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Ben and Lily went to the park with Mom. They saw a huge pond with many ducks. Ben and Lily liked ducks. They wanted to feed them.

"Mom, can we give them some bread?" Lily asked.

"Sorry, sweetie, we don't have any bread. But we have some olives. Do you think they will like olives?" Mom said.

"Let's try!" Ben said. He took an olive from Mom's bag and threw it into the pond. A duck saw the olive and swam to get it. It picked up the olive with its beak and ate it.

"Yay! The duck likes olives!" Ben cheered.

"Me too! Me too!" Lily said. She took another olive and threw it into the pond. Another duck swam to get it. It also ate the olive.

"Wow! The ducks love olives!" Lily said.

"Can we swim with the ducks, Mom?" Ben asked.

"No, honey, the pond is too deep and cold for you. And the ducks might not like it. They need their space. But you can watch them swim and quack. They are very happy." Mom said.

"Okay, Mom. We will watch them. They are very cute." Ben said.

"Yes, they are. And you are very kind to share your olives with them." Mom said.

Ben and Lily smiled. They sat on the grass and watched the ducks swim and eat olives. They had a lot of fun at the park.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_000978_chunk_000**

```text
Ben and Lily went to the park with Mom. They saw a huge pond with many ducks. Ben and Lily liked ducks. They wanted to feed them.

"Mom, can we give them some bread?" Lily asked.

"Sorry, sweetie, we don't have any bread. But we have some olives. Do you think they will like olives?" Mom said.

"Let's try!" Ben said. He took an olive from Mom's bag and threw it into the pond. A duck saw the olive and swam to get it. It picked up the olive with its beak and ate it.

"Yay!
```

**story_000978_chunk_001**

```text
 the pond. A duck saw the olive and swam to get it. It picked up the olive with its beak and ate it.

"Yay! The duck likes olives!" Ben cheered.

"Me too! Me too!" Lily said. She took another olive and threw it into the pond. Another duck swam to get it. It also ate the olive.

"Wow! The ducks love olives!" Lily said.

"Can we swim with the ducks, Mom?" Ben asked.

"No, honey, the pond is too deep and cold for you. And the ducks might not like it. They need their space.
```

**story_000978_chunk_002**

```text
 Mom?" Ben asked.

"No, honey, the pond is too deep and cold for you. And the ducks might not like it. They need their space. But you can watch them swim and quack. They are very happy." Mom said.

"Okay, Mom. We will watch them. They are very cute." Ben said.

"Yes, they are. And you are very kind to share your olives with them." Mom said.

Ben and Lily smiled. They sat on the grass and watched the ducks swim and eat olives. They had a lot of fun at the park.
```


## q011

问题：What material did Jack want to use to make something special with Jill's help?

预期答案：Clay.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there were two friends: Jack and Jill. Jack had a brilliant idea. He wanted to make something special using clay.

He asked Jill for help to match the pieces of clay together. She was happy to join in and the two began to make something exciting.

With Jill's help, shapes and designs began to appear from the clay. Hours passed, and eventually the friends had made something really fantastic. It was a beautiful clay castle.

They stood back to admire their work. Jill said it was brilliant, and Jack was very proud.

The castle was the perfect match for their creativity! They both knew it was something special. The end.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_001097_chunk_000**

```text
Once upon a time, there were two friends: Jack and Jill. Jack had a brilliant idea. He wanted to make something special using clay.

He asked Jill for help to match the pieces of clay together. She was happy to join in and the two began to make something exciting.

With Jill's help, shapes and designs began to appear from the clay. Hours passed, and eventually the friends had made something really fantastic. It was a beautiful clay castle.

They stood back to admire their work. Jill said it was brilliant, and Jack was very proud.

The castle was the perfect match for their creativity! They both knew it was something
```

**story_001097_chunk_001**

```text
 admire their work. Jill said it was brilliant, and Jack was very proud.

The castle was the perfect match for their creativity! They both knew it was something special. The end.
```


## q012

问题：Why did the man feel guilty after asking his wife to come on a trip?

预期答案：She said no, and he felt guilty about wanting to go without her.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time there was a man who had a wife. One day, the man wanted to go on a trip. He asked his wife to come with him, but she said no. The man felt guilty for wanting to go without her. He thought about it for a long time and decided to lead his wife on the journey instead. 

When they arrived at their destination, they both had a wonderful time. They explored the area and looked at all the amazing sights. They were very happy to be together. 

The man was happy he had decided to lead his wife on this journey. He knew that he did the right thing, and he was no longer feeling guilty. From then on, they decided to make more trips together. They were so happy to be together that each journey was even more special than the last.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_001240_chunk_000**

```text
Once upon a time there was a man who had a wife. One day, the man wanted to go on a trip. He asked his wife to come with him, but she said no. The man felt guilty for wanting to go without her. He thought about it for a long time and decided to lead his wife on the journey instead. 

When they arrived at their destination, they both had a wonderful time. They explored the area and looked at all the amazing sights. They were very happy to be together. 

The man was happy he had decided to lead his wife on this journey. He knew that he did the right thing
```

**story_001240_chunk_001**

```text
 They were very happy to be together. 

The man was happy he had decided to lead his wife on this journey. He knew that he did the right thing, and he was no longer feeling guilty. From then on, they decided to make more trips together. They were so happy to be together that each journey was even more special than the last.
```


## q013

问题：Why was Spot hurt and crying after Tom threw a ball for him in the park?

预期答案：A frightened wild cat bit Spot.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, in a modern house, lived a boy named Tom. He had a wild dog named Spot. They loved to play outside in the sun.

One day, Tom and Spot went to the park. They saw a big tree. Tom wanted to climb the tree, but Spot wanted to play with a ball. So, Tom threw the ball for Spot to catch.

When Spot ran to get the ball, he saw a wild cat. Spot wanted to play with the cat, but the cat didn't want to play. The cat was scared, and it bit Spot. Spot cried, and Tom ran to help him. They went home, but Spot was hurt and sad. The end.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_001385_chunk_000**

```text
Once upon a time, in a modern house, lived a boy named Tom. He had a wild dog named Spot. They loved to play outside in the sun.

One day, Tom and Spot went to the park. They saw a big tree. Tom wanted to climb the tree, but Spot wanted to play with a ball. So, Tom threw the ball for Spot to catch.

When Spot ran to get the ball, he saw a wild cat. Spot wanted to play with the cat, but the cat didn't want to play. The cat was scared, and it bit Spot. Spot cried, and Tom ran to help him.
```

**story_001385_chunk_001**

```text
 the cat, but the cat didn't want to play. The cat was scared, and it bit Spot. Spot cried, and Tom ran to help him. They went home, but Spot was hurt and sad. The end.
```


## q014

问题：What caused the cat to lose the perfect name it had attached to a tree?

预期答案：A storm blew the name away.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a gray cat. One day, the cat wanted to give itself a name. So, it attached itself to a nearby tree to begin thinking.

The tree was tall and green, and the cat thought and thought. Eventually, it came up with the perfect name. The cat was so proud of its name that it did not want anyone else to know it.

The cat kept thinking and eventually attached its name to the tree. The cat felt so happy to have found a safe place for its name. 

But one day, a big storm hit the tree and the wind blew the name away. The cat searched everywhere but it couldn't find its name again. The cat was sad because it knew it could never find the perfect name again.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_001529_chunk_000**

```text
Once upon a time, there was a gray cat. One day, the cat wanted to give itself a name. So, it attached itself to a nearby tree to begin thinking.

The tree was tall and green, and the cat thought and thought. Eventually, it came up with the perfect name. The cat was so proud of its name that it did not want anyone else to know it.

The cat kept thinking and eventually attached its name to the tree. The cat felt so happy to have found a safe place for its name. 

But one day, a big storm hit the tree and the wind blew the name away. The cat
```

**story_001529_chunk_001**

```text
 happy to have found a safe place for its name. 

But one day, a big storm hit the tree and the wind blew the name away. The cat searched everywhere but it couldn't find its name again. The cat was sad because it knew it could never find the perfect name again.
```


## q015

问题：How old was the youngest child in the wealthy family who also wanted to go to university?

预期答案：Three years old.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once there was a wealthy family with three kids. Two of them were in university, but the youngest one was only three. He wanted to go to university too!

One day, the three university students decided to take the youngest one with them on a fun day out. As they drove to the university, the little kid cheered with joy. 

When they arrived, the little kid wanted to explore everywhere. He ran around and screamed with excitement!

The university students showed him all the places and got him some ice cream. He was having so much fun!

At the end of the day, the family drove home and the little kid felt so happy. He dreamed of one day going to university too.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_001662_chunk_000**

```text
Once there was a wealthy family with three kids. Two of them were in university, but the youngest one was only three. He wanted to go to university too!

One day, the three university students decided to take the youngest one with them on a fun day out. As they drove to the university, the little kid cheered with joy. 

When they arrived, the little kid wanted to explore everywhere. He ran around and screamed with excitement!

The university students showed him all the places and got him some ice cream. He was having so much fun!

At the end of the day, the family drove home and the little kid felt so
```

**story_001662_chunk_001**

```text
 places and got him some ice cream. He was having so much fun!

At the end of the day, the family drove home and the little kid felt so happy. He dreamed of one day going to university too.
```


## q016

问题：What helped Amy feel safe and loved during the frightening storm?

预期答案：Her mother held her in her arms.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a little girl called Amy. She was very hungry. Her tummy felt funny and all she wanted was something yummy. So she went outside to look for something to eat.

As she walked, the sky grew dark and a storm began. Big rain drops started to fall and thunder clapped in the sky. Amy was scared and started to cry.

But then, she heard a voice from behind, saying "Amy, don't worry". When she looked back, she saw her Mommy. Her Mommy opened her umbrella and said, "Come here, I will squeeze you tight".

Amy felt much better when her Mommy held her. She knew she felt safe and loved in her Mommy's arms.

From that day on, Amy learned that when times were tough and the storm was scary, all she had to do was squeeze her Mommy and she would feel safe. This taught her that love was one of the most important things in life.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_001795_chunk_000**

```text
Once upon a time, there was a little girl called Amy. She was very hungry. Her tummy felt funny and all she wanted was something yummy. So she went outside to look for something to eat.

As she walked, the sky grew dark and a storm began. Big rain drops started to fall and thunder clapped in the sky. Amy was scared and started to cry.

But then, she heard a voice from behind, saying "Amy, don't worry". When she looked back, she saw her Mommy. Her Mommy opened her umbrella and said, "Come here, I will squeeze you tight".

Amy felt much
```

**story_001795_chunk_001**

```text
 she looked back, she saw her Mommy. Her Mommy opened her umbrella and said, "Come here, I will squeeze you tight".

Amy felt much better when her Mommy held her. She knew she felt safe and loved in her Mommy's arms.

From that day on, Amy learned that when times were tough and the storm was scary, all she had to do was squeeze her Mommy and she would feel safe. This taught her that love was one of the most important things in life.
```


## q017

问题：Why did the teacher tell Mary to put away the candy she was sharing in the classroom?

预期答案：Snacks could spoil everyone's appetite before lunch.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Mary was playing in her classroom when she had an idea. She was going to spoil all her classmates! She took three candy bars and started sharing them out, one bar to everyone else in her class. 

But then a teacher came in and saw what was happening. "Mary," she said, "what are you doing? You can't share out candy in the classroom."

Mary was shocked. She said, "But everyone else was going to be so happy I was sharing it."

But the teacher said, "It's not nice to be so ignorant. You could spoil everyone's appetite before lunch if you give them snacks now. Now, why don't you put the candy away?"

Mary felt really bad, but she knew the teacher was right. She put the candy away and decided that in future, she would act more kindly and not be so ignorant.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_001920_chunk_000**

```text
Mary was playing in her classroom when she had an idea. She was going to spoil all her classmates! She took three candy bars and started sharing them out, one bar to everyone else in her class. 

But then a teacher came in and saw what was happening. "Mary," she said, "what are you doing? You can't share out candy in the classroom."

Mary was shocked. She said, "But everyone else was going to be so happy I was sharing it."

But the teacher said, "It's not nice to be so ignorant. You could spoil everyone's appetite before lunch if you give them snacks now.
```

**story_001920_chunk_001**

```text
 it."

But the teacher said, "It's not nice to be so ignorant. You could spoil everyone's appetite before lunch if you give them snacks now. Now, why don't you put the candy away?"

Mary felt really bad, but she knew the teacher was right. She put the candy away and decided that in future, she would act more kindly and not be so ignorant.
```


## q018

问题：What did Sarah do after her mother caught her grabbing candy from the jar without permission?

预期答案：She put the candy back in the jar.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once there was a little girl named Sarah. She was three years old. One day, Sarah was in the kitchen. She saw some candy that was in a jar. 

"I want to eat the candy," she thought. 

But Sarah knew she wasn't allowed to have any candy without asking her parents first. She knew she had to use the words 'Please' and 'Thank you'. So Sarah asked her mom if she could have some candy.

"No, Sarah," her mom said. "It's too much candy. You can have something else."

Sarah was not happy. She really wanted the candy. But she was ashamed to ask her mom again. So Sarah used her sneaky plan. She reached into the jar and grabbed a handful of candy.

Then Sarah heard a loud voice. It was her mom.

"Sarah! Put the candy back! We don't take things without asking!"

Sarah felt embarrassed. She put the candy back in the jar, and she knew she had been wrong. She never used candy without asking again.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_002045_chunk_000**

```text
Once there was a little girl named Sarah. She was three years old. One day, Sarah was in the kitchen. She saw some candy that was in a jar. 

"I want to eat the candy," she thought. 

But Sarah knew she wasn't allowed to have any candy without asking her parents first. She knew she had to use the words 'Please' and 'Thank you'. So Sarah asked her mom if she could have some candy.

"No, Sarah," her mom said. "It's too much candy. You can have something else."

Sarah was not happy. She really wanted the candy. But she was ashamed to
```

**story_002045_chunk_001**

```text
 mom said. "It's too much candy. You can have something else."

Sarah was not happy. She really wanted the candy. But she was ashamed to ask her mom again. So Sarah used her sneaky plan. She reached into the jar and grabbed a handful of candy.

Then Sarah heard a loud voice. It was her mom.

"Sarah! Put the candy back! We don't take things without asking!"

Sarah felt embarrassed. She put the candy back in the jar, and she knew she had been wrong. She never used candy without asking again.
```


## q019

问题：Under what condition did the man agree to forgive Sam and Ben in the kayak story?

预期答案：They had to promise to be good and respect other people's things.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Ben and Sam were best friends. They liked to play outside and go on adventures. One day, they saw a kayak by the lake. It was red and shiny and looked like fun.

"Wow, look at that kayak!" Ben said. "Can we try it?"

"I don't know," Sam said. "It's not ours. Maybe someone left it here."

"Or maybe they don't want it anymore," Ben said. "Let's go and see."

They ran to the kayak and touched it. It was smooth and hard. They looked inside and saw two paddles.

"Let's go for a ride," Ben said. "It will be fun."

"But what if someone comes back and gets angry?" Sam said. "We should ask first."

"Who are we going to ask?" Ben said. "There's no one here. Come on, don't be scared."

Ben climbed into the kayak and grabbed a paddle. He waited for Sam to join him.

Sam looked around. He felt bad. He knew it was wrong to take something that was not theirs. He wanted to have fun, but he also wanted to be good.

"Ben, I don't think we should do this," Sam said. "It's not nice. Let's go and play something else."

Ben frowned. He was annoyed. He wanted to go on the kayak. He thought Sam was being silly.

"Fine, be a baby," Ben said. "I'm going without you."

He pushed the kayak into the water and started to paddle. He felt happy and free. He didn't care about Sam.

Sam watched Ben go. He felt sad and lonely. He wished Ben would listen to him. He hoped Ben would be safe.

Soon, Ben was far away from the shore. He looked around and saw the lake was big and beautiful. He saw fish and birds and trees. He smiled and paddled faster.

But then, he heard a loud voice.

"Hey, you! Get out of my kayak!"

Ben turned and saw a man on the shore. He was big and angry. He was waving his arms and shouting.

Ben felt scared. He realized he had made a mistake. He had taken someone else's kayak. He had been bad.

He tried to paddle back, but it was hard. The wind was blowing and the water was choppy. He felt tired and sorry.

The man ran into the water and swam towards Ben. He reached the kayak and grabbed it. He pulled Ben out and dragged him to the shore.

He was very mad. He yelled at Ben and asked him why he had taken his kayak. He said he had been generous and let other people use his kayak, but only if they asked first. He said Ben had been rude and selfish.

Ben felt ashamed. He didn't know what to say. He wished he had listened to Sam. He wished he had been good.

He looked at Sam, who was still on the shore. Sam looked at him with pity and concern. He walked over to Ben and the man.

He said he was sorry for what Ben had done. He said they were friends and they had seen the kayak and wanted to try it. He said Ben had not listened to him and had gone without asking. He said he had tried to stop him and had stayed behind.

He said they had learned their lesson and they would never do it again. He said they were sorry and they hoped the man would forgive them.

The man looked at Sam and Ben. He saw they were young and scared. He saw they had made a mistake and they were sorry. He felt his anger fade.

He said he was glad Sam had been honest and brave. He said he was glad Ben had come back and had apologized. He said he would forgive them, but only if they promised to be good and to respect other people's things.

He said he would be generous and let them use his kayak, but only if they asked first and followed his rules. He said he would teach them how to paddle and how to be safe on the water.

He said he hoped they would enjoy the kayak and the lake, but also learn to be good and kind.

Sam and Ben nodded. They said they were sorry and they thanked the man. They said they would be good and they would respect his kayak. They said they would like to learn from him and have fun with him.

They hugged each other and smiled. They felt happy and relieved. They had made a new friend and they had learned a valuable lesson.

They had learned to be good and generous.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_002137_chunk_000**

```text
Ben and Sam were best friends. They liked to play outside and go on adventures. One day, they saw a kayak by the lake. It was red and shiny and looked like fun.

"Wow, look at that kayak!" Ben said. "Can we try it?"

"I don't know," Sam said. "It's not ours. Maybe someone left it here."

"Or maybe they don't want it anymore," Ben said. "Let's go and see."

They ran to the kayak and touched it. It was smooth and hard. They looked inside and saw two paddles.

"Let's go for a ride," Ben
```

**story_002137_chunk_001**

```text
 ran to the kayak and touched it. It was smooth and hard. They looked inside and saw two paddles.

"Let's go for a ride," Ben said. "It will be fun."

"But what if someone comes back and gets angry?" Sam said. "We should ask first."

"Who are we going to ask?" Ben said. "There's no one here. Come on, don't be scared."

Ben climbed into the kayak and grabbed a paddle. He waited for Sam to join him.

Sam looked around. He felt bad. He knew it was wrong to take something that was not theirs. He wanted to have
```

**story_002137_chunk_002**

```text
 waited for Sam to join him.

Sam looked around. He felt bad. He knew it was wrong to take something that was not theirs. He wanted to have fun, but he also wanted to be good.

"Ben, I don't think we should do this," Sam said. "It's not nice. Let's go and play something else."

Ben frowned. He was annoyed. He wanted to go on the kayak. He thought Sam was being silly.

"Fine, be a baby," Ben said. "I'm going without you."

He pushed the kayak into the water and started to paddle. He felt happy and free.
```

**story_002137_chunk_003**

```text
 be a baby," Ben said. "I'm going without you."

He pushed the kayak into the water and started to paddle. He felt happy and free. He didn't care about Sam.

Sam watched Ben go. He felt sad and lonely. He wished Ben would listen to him. He hoped Ben would be safe.

Soon, Ben was far away from the shore. He looked around and saw the lake was big and beautiful. He saw fish and birds and trees. He smiled and paddled faster.

But then, he heard a loud voice.

"Hey, you! Get out of my kayak!"

Ben turned and saw a man
```

**story_002137_chunk_004**

```text
 smiled and paddled faster.

But then, he heard a loud voice.

"Hey, you! Get out of my kayak!"

Ben turned and saw a man on the shore. He was big and angry. He was waving his arms and shouting.

Ben felt scared. He realized he had made a mistake. He had taken someone else's kayak. He had been bad.

He tried to paddle back, but it was hard. The wind was blowing and the water was choppy. He felt tired and sorry.

The man ran into the water and swam towards Ben. He reached the kayak and grabbed it. He pulled Ben out and
```

**story_002137_chunk_005**

```text
. He felt tired and sorry.

The man ran into the water and swam towards Ben. He reached the kayak and grabbed it. He pulled Ben out and dragged him to the shore.

He was very mad. He yelled at Ben and asked him why he had taken his kayak. He said he had been generous and let other people use his kayak, but only if they asked first. He said Ben had been rude and selfish.

Ben felt ashamed. He didn't know what to say. He wished he had listened to Sam. He wished he had been good.

He looked at Sam, who was still on the shore. Sam looked
```

**story_002137_chunk_006**

```text
 to say. He wished he had listened to Sam. He wished he had been good.

He looked at Sam, who was still on the shore. Sam looked at him with pity and concern. He walked over to Ben and the man.

He said he was sorry for what Ben had done. He said they were friends and they had seen the kayak and wanted to try it. He said Ben had not listened to him and had gone without asking. He said he had tried to stop him and had stayed behind.

He said they had learned their lesson and they would never do it again. He said they were sorry and they hoped the man
```

**story_002137_chunk_007**

```text
 stop him and had stayed behind.

He said they had learned their lesson and they would never do it again. He said they were sorry and they hoped the man would forgive them.

The man looked at Sam and Ben. He saw they were young and scared. He saw they had made a mistake and they were sorry. He felt his anger fade.

He said he was glad Sam had been honest and brave. He said he was glad Ben had come back and had apologized. He said he would forgive them, but only if they promised to be good and to respect other people's things.

He said he would be generous and let them use
```

**story_002137_chunk_008**

```text
 said he would forgive them, but only if they promised to be good and to respect other people's things.

He said he would be generous and let them use his kayak, but only if they asked first and followed his rules. He said he would teach them how to paddle and how to be safe on the water.

He said he hoped they would enjoy the kayak and the lake, but also learn to be good and kind.

Sam and Ben nodded. They said they were sorry and they thanked the man. They said they would be good and they would respect his kayak. They said they would like to learn from him and have fun with
```

**story_002137_chunk_009**

```text
 and they thanked the man. They said they would be good and they would respect his kayak. They said they would like to learn from him and have fun with him.

They hugged each other and smiled. They felt happy and relieved. They had made a new friend and they had learned a valuable lesson.

They had learned to be good and generous.
```


## q020

问题：Why did Lily refuse to go to her bedroom when her mother said it was bedtime?

预期答案：Her bedroom was too cold.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a little girl named Lily. She loved to play and have fun. One night, Lily's mommy told her it was time for bed. Lily didn't want to go to her bedroom because it was cold in there.

Lily said, "Mommy, I don't want to go to my bedroom. It's too cold in there."

Mommy said, "Lily, you need to behave and go to bed."

Lily went to her bedroom but she was still cold. She got out of bed and went to the living room to tell her mommy. Mommy was upset because Lily wasn't behaving. She told Lily to go back to bed.

Lily went back to her bedroom but she was still cold. She couldn't sleep, so she got up and went to the living room again. This time, mommy was really upset. She told Lily to go back to bed and stay there.

Lily went back to her bedroom but she was still cold and couldn't sleep. She started to cry. Suddenly, she heard a loud noise outside. She was scared and didn't know what to do. She wanted her mommy, but she was too scared to leave her bedroom. Unfortunately, the bad ending is that Lily was too scared to get help and ended up getting hurt.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_002205_chunk_000**

```text
Once upon a time, there was a little girl named Lily. She loved to play and have fun. One night, Lily's mommy told her it was time for bed. Lily didn't want to go to her bedroom because it was cold in there.

Lily said, "Mommy, I don't want to go to my bedroom. It's too cold in there."

Mommy said, "Lily, you need to behave and go to bed."

Lily went to her bedroom but she was still cold. She got out of bed and went to the living room to tell her mommy. Mommy was upset because Lily wasn
```

**story_002205_chunk_001**

```text
 to her bedroom but she was still cold. She got out of bed and went to the living room to tell her mommy. Mommy was upset because Lily wasn't behaving. She told Lily to go back to bed.

Lily went back to her bedroom but she was still cold. She couldn't sleep, so she got up and went to the living room again. This time, mommy was really upset. She told Lily to go back to bed and stay there.

Lily went back to her bedroom but she was still cold and couldn't sleep. She started to cry. Suddenly, she heard a loud noise outside. She was scared
```

**story_002205_chunk_002**

```text
 went back to her bedroom but she was still cold and couldn't sleep. She started to cry. Suddenly, she heard a loud noise outside. She was scared and didn't know what to do. She wanted her mommy, but she was too scared to leave her bedroom. Unfortunately, the bad ending is that Lily was too scared to get help and ended up getting hurt.
```


## q021

问题：What was the name of the man's dog that met Tim and Lily and liked to run and play?

预期答案：Spot.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Tim and Lily are friends. They like to play in the park. They see a big circle on the grass. It is made of stones.

"Let's run around the circle!" Tim says.

"OK!" Lily says. They hold hands and run. They run fast and slow. They run inside and outside the circle. They laugh and have fun.

They see a dog. The dog is brown and furry. The dog runs to them. He wants to play too.

"Hello, dog!" Tim says. He pets the dog. The dog licks his face.

"Can we keep him?" Lily asks.

"I don't know," Tim says. "Maybe we can ask his owner."

They look around. They see a man. The man is holding a leash. The leash is for the dog.

"Is this your dog?" Tim asks the man.

"Yes, he is. His name is Spot. He likes to run and play," the man says.

"He is a nice dog. We like him," Lily says.

"I'm glad you do. He likes you too. Do you want to play with him for a while?" the man asks.

"Yes, please!" Tim and Lily say.

They play with Spot and the man. They run and throw a ball. They make a new friend. They are very glad.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_002292_chunk_000**

```text
Tim and Lily are friends. They like to play in the park. They see a big circle on the grass. It is made of stones.

"Let's run around the circle!" Tim says.

"OK!" Lily says. They hold hands and run. They run fast and slow. They run inside and outside the circle. They laugh and have fun.

They see a dog. The dog is brown and furry. The dog runs to them. He wants to play too.

"Hello, dog!" Tim says. He pets the dog. The dog licks his face.

"Can we keep him?" Lily asks.

"I don't
```

**story_002292_chunk_001**

```text
"Hello, dog!" Tim says. He pets the dog. The dog licks his face.

"Can we keep him?" Lily asks.

"I don't know," Tim says. "Maybe we can ask his owner."

They look around. They see a man. The man is holding a leash. The leash is for the dog.

"Is this your dog?" Tim asks the man.

"Yes, he is. His name is Spot. He likes to run and play," the man says.

"He is a nice dog. We like him," Lily says.

"I'm glad you do. He likes you too. Do you want to
```

**story_002292_chunk_002**

```text
 the man says.

"He is a nice dog. We like him," Lily says.

"I'm glad you do. He likes you too. Do you want to play with him for a while?" the man asks.

"Yes, please!" Tim and Lily say.

They play with Spot and the man. They run and throw a ball. They make a new friend. They are very glad.
```


## q022

问题：What instrument did Timmy and Billy bang on when they played music together every day?

预期答案：A drum.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a boy named Timmy. Timmy loved to play with his huge drum. He would bang on it all day long and laugh when he made loud noises. 

One day, Timmy's friend Billy came over to play. Billy saw Timmy's drum and said, "Wow, that's a big drum!" Timmy said, "Yes, it's huge! Do you want to play with it?" 

Billy nodded his head and started to bang on the drum. Timmy laughed and said, "You're really good at playing the drum, Billy!" Billy smiled and said, "Thanks, Timmy. I like playing with your drum." 

From that day on, Timmy and Billy played together every day. They would bang on the drum and laugh together. They were the best of friends and they loved playing music together. The end.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_002365_chunk_000**

```text
Once upon a time, there was a boy named Timmy. Timmy loved to play with his huge drum. He would bang on it all day long and laugh when he made loud noises. 

One day, Timmy's friend Billy came over to play. Billy saw Timmy's drum and said, "Wow, that's a big drum!" Timmy said, "Yes, it's huge! Do you want to play with it?" 

Billy nodded his head and started to bang on the drum. Timmy laughed and said, "You're really good at playing the drum, Billy!" Billy smiled and said, "Thanks
```

**story_002365_chunk_001**

```text
 started to bang on the drum. Timmy laughed and said, "You're really good at playing the drum, Billy!" Billy smiled and said, "Thanks, Timmy. I like playing with your drum." 

From that day on, Timmy and Billy played together every day. They would bang on the drum and laugh together. They were the best of friends and they loved playing music together. The end.
```


## q023

问题：Where did the ball get stuck after flying over Timmy's head during a game of catch?

预期答案：In a nearby net.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a little boy named Timmy. Timmy loved to play outside with his friends. One day, Timmy and his friends decided to play a game of catch. Timmy tried his best to catch the ball, but it kept slipping out of his hands. 

Suddenly, the ball flew over Timmy's head and landed in a nearby net. Timmy ran over to the net and tried to get the ball out, but it was stuck. He pulled and pulled, but the ball wouldn't budge. 

Timmy's friends came over to help him. They all tried to get the ball out of the net, but it was no use. Timmy's arm started to hurt from pulling so hard. Just when they thought they would never get the ball back, Timmy's big brother came to the rescue. He easily got the ball out of the net and gave it back to Timmy. Timmy was so happy and grateful to his brother for helping him.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_002511_chunk_000**

```text
Once upon a time, there was a little boy named Timmy. Timmy loved to play outside with his friends. One day, Timmy and his friends decided to play a game of catch. Timmy tried his best to catch the ball, but it kept slipping out of his hands. 

Suddenly, the ball flew over Timmy's head and landed in a nearby net. Timmy ran over to the net and tried to get the ball out, but it was stuck. He pulled and pulled, but the ball wouldn't budge. 

Timmy's friends came over to help him. They all tried to get the ball
```

**story_002511_chunk_001**

```text
. He pulled and pulled, but the ball wouldn't budge. 

Timmy's friends came over to help him. They all tried to get the ball out of the net, but it was no use. Timmy's arm started to hurt from pulling so hard. Just when they thought they would never get the ball back, Timmy's big brother came to the rescue. He easily got the ball out of the net and gave it back to Timmy. Timmy was so happy and grateful to his brother for helping him.
```


## q024

问题：What bit Julia on the arm while she was helping a bird that was afraid of lightning?

预期答案：A tiny yellow snake.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time there was a brave little girl named Julia. She lived in a small town near the sea.

One day, dark clouds formed in the sky. Julia saw lightning and heard thunder. She was scared, but she was brave and wanted to see the storm closely.

Julia went outside and noticed a big, dangerous tree. On the very top of the tree sat a bird. Suddenly, she heard the bird chirping.

â€œWhat are you doing up there?â€ asked Julia.

â€œIâ€™m scared of the lightning,â€ said the bird. â€œItâ€™s too dangerous for me to fly away.â€

Julia reached up and grabbed the bird gently. â€œDonâ€™t worry,â€ she said. â€œI will keep you safe.â€

The bird smiled and said, â€œThank you.â€

Just then, Julia felt a sharp bite on her arm. She looked down and saw a tiny yellow snake.

â€œThatâ€™s a dangerous snake,â€ said the bird. â€œHe wants to bite you.â€

Julia quickly put the bird back in the tree and ran away. She had been brave, but now she was safe.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_002640_chunk_000**

```text
Once upon a time there was a brave little girl named Julia. She lived in a small town near the sea.

One day, dark clouds formed in the sky. Julia saw lightning and heard thunder. She was scared, but she was brave and wanted to see the storm closely.

Julia went outside and noticed a big, dangerous tree. On the very top of the tree sat a bird. Suddenly, she heard the bird chirping.

â€œWhat are you doing up there?â€ asked Julia.

â€œIâ€™m scared of the lightning,â€ said the bird. â€œItâ€™s
```

**story_002640_chunk_001**

```text
 there?â€ asked Julia.

â€œIâ€™m scared of the lightning,â€ said the bird. â€œItâ€™s too dangerous for me to fly away.â€

Julia reached up and grabbed the bird gently. â€œDonâ€™t worry,â€ she said. â€œI will keep you safe.â€

The bird smiled and said, â€œThank you.â€

Just then, Julia felt a sharp bite on her arm. She looked down and saw a tiny yellow snake.

â€œThatâ€™s a dangerous snake,â
```

**story_002640_chunk_002**

```text
, Julia felt a sharp bite on her arm. She looked down and saw a tiny yellow snake.

â€œThatâ€™s a dangerous snake,â€ said the bird. â€œHe wants to bite you.â€

Julia quickly put the bird back in the tree and ran away. She had been brave, but now she was safe.
```


## q025

问题：What did Sophie discover shining in the darkness after striking it with her stick?

预期答案：A diamond.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time there was a small girl named Sophie. She wanted to find a mine to explore.

One day she went on a walk and saw a mine. She was very excited. 

Sophie entered the mine and looked around. She had a special stick in her hand. Suddenly, something sparkled in the dark. What could it be? 

Sophie struck her stick against it and the sparkles stopped. She looked closer and saw something was shining in the darkness. It was a diamond! 

Surprised, Sophie said out loud, "I found a diamond!"

Suddenly, she heard a voice. It came from a man who was hiding in the corner of the mine. He said, "Well, this diamond is mine." 

Sophie was not scared. She was thoughtful. She asked the man, "If I give the diamond to you, can I explore the mine?" 

The man thought for a moment and said, "Yes, but be careful."

Sophie thanked him and gave the diamond to the man. She explored the mine and had a great adventure. She went home with many stories to tell.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_002763_chunk_000**

```text
Once upon a time there was a small girl named Sophie. She wanted to find a mine to explore.

One day she went on a walk and saw a mine. She was very excited. 

Sophie entered the mine and looked around. She had a special stick in her hand. Suddenly, something sparkled in the dark. What could it be? 

Sophie struck her stick against it and the sparkles stopped. She looked closer and saw something was shining in the darkness. It was a diamond! 

Surprised, Sophie said out loud, "I found a diamond!"

Suddenly, she heard a voice. It came from
```

**story_002763_chunk_001**

```text
. It was a diamond! 

Surprised, Sophie said out loud, "I found a diamond!"

Suddenly, she heard a voice. It came from a man who was hiding in the corner of the mine. He said, "Well, this diamond is mine." 

Sophie was not scared. She was thoughtful. She asked the man, "If I give the diamond to you, can I explore the mine?" 

The man thought for a moment and said, "Yes, but be careful."

Sophie thanked him and gave the diamond to the man. She explored the mine and had a great adventure. She went home
```

**story_002763_chunk_002**

```text
 "Yes, but be careful."

Sophie thanked him and gave the diamond to the man. She explored the mine and had a great adventure. She went home with many stories to tell.
```


## q026

问题：What were Sally and her family painting when Grandma asked to visit?

预期答案：A big yellow sun.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a yellow house. In the house, there was a girl named Sally. Sally loved to paint. She had a lot of fun making pretty pictures.

One day, Sally's friend Timmy came over to play. They decided to paint together. Timmy said, "Sally, let's paint a big, yellow sun!" Sally agreed, and they started to paint the sun on a big piece of paper.

While they were painting, the telephone rang. Sally picked it up and said, "Hello?" It was her grandma on the other side. Grandma said, "Hi Sally! I miss you. Can I come visit you today?" Sally was very happy and said, "Yes, Grandma! Please come. We are painting a big, yellow sun!"

Grandma came over, and they all painted together. They had a great time, and the big, yellow sun was very pretty. At the end of the day, they hung the painting on the wall, and it made everyone smile.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_002893_chunk_000**

```text
Once upon a time, there was a yellow house. In the house, there was a girl named Sally. Sally loved to paint. She had a lot of fun making pretty pictures.

One day, Sally's friend Timmy came over to play. They decided to paint together. Timmy said, "Sally, let's paint a big, yellow sun!" Sally agreed, and they started to paint the sun on a big piece of paper.

While they were painting, the telephone rang. Sally picked it up and said, "Hello?" It was her grandma on the other side. Grandma said, "Hi Sally! I miss you
```

**story_002893_chunk_001**

```text
 telephone rang. Sally picked it up and said, "Hello?" It was her grandma on the other side. Grandma said, "Hi Sally! I miss you. Can I come visit you today?" Sally was very happy and said, "Yes, Grandma! Please come. We are painting a big, yellow sun!"

Grandma came over, and they all painted together. They had a great time, and the big, yellow sun was very pretty. At the end of the day, they hung the painting on the wall, and it made everyone smile.
```


## q027

问题：How did Lily's mother help her read the library book with a hairy monster on its cover?

预期答案：She helped Lily sound out the words.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a little girl named Lily. Lily loved to read books. One day, her mom took her to the library. The library was a big building with lots of books. 

Lily saw a book with a picture of a hairy monster on it. She wanted to read it, but she didn't understand the words. Her mom helped her sound out the words, and soon Lily understood the story. 

Lily loved going to the library and finding new books to read. She was so happy that she could understand the stories all by herself. And she even found some more books about hairy monsters!
```

### 全部目标故事文段（候选外的文段也需检查）

**story_003037_chunk_000**

```text
Once upon a time, there was a little girl named Lily. Lily loved to read books. One day, her mom took her to the library. The library was a big building with lots of books. 

Lily saw a book with a picture of a hairy monster on it. She wanted to read it, but she didn't understand the words. Her mom helped her sound out the words, and soon Lily understood the story. 

Lily loved going to the library and finding new books to read. She was so happy that she could understand the stories all by herself. And she even found some more books about hairy monsters!
```


## q028

问题：What activity did Amy's mother suggest instead of jumping near the enormous tree in the park?

预期答案：Jogging around the park.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
One day, Amy was feeling very sick. She had a big fever and felt very weak. Her Mommy gave her some medicine to make her feel better. After taking it, Amy felt much better. 

Her Mommy said, "Let's go outside to get some fresh air." Together, they went to the park. There was an enormous tree in the park, and Amy was so excited. She ran over to it and jumped.

Mommy said, "We can't jump today. Let's go for a jog around the park instead!" Amy was surprise, but liked the idea. Together, they jogged around the park. It was so much fun! 

Amy was so happy that she felt better and that they had jogged around the park. Soon it was time to go home, but Amy had a lot of energy still. 

Mommy said, "Let's stay here a while longer and jog some more!" So they jogged around the park one more time, and then they went home. 

That was the best day ever!
```

### 全部目标故事文段（候选外的文段也需检查）

**story_003178_chunk_000**

```text
One day, Amy was feeling very sick. She had a big fever and felt very weak. Her Mommy gave her some medicine to make her feel better. After taking it, Amy felt much better. 

Her Mommy said, "Let's go outside to get some fresh air." Together, they went to the park. There was an enormous tree in the park, and Amy was so excited. She ran over to it and jumped.

Mommy said, "We can't jump today. Let's go for a jog around the park instead!" Amy was surprise, but liked the idea. Together, they jogged around the park
```

**story_003178_chunk_001**

```text
't jump today. Let's go for a jog around the park instead!" Amy was surprise, but liked the idea. Together, they jogged around the park. It was so much fun! 

Amy was so happy that she felt better and that they had jogged around the park. Soon it was time to go home, but Amy had a lot of energy still. 

Mommy said, "Let's stay here a while longer and jog some more!" So they jogged around the park one more time, and then they went home. 

That was the best day ever!
```


## q029

问题：Why did the adventurous bear resist eating the tasty-looking treat in the forest?

预期答案：He realized it was poison.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time there was an adventurous bear. One day, the bear was walking through the forest when he came across a yummy treat. The treat looked tasty and the bear wanted to eat it. But then he realized that it was poison! The bear resisted the temptation to eat it.

The bear then heard a voice calling him. He looked up and saw a beautiful bird in a nearby tree. The bird asked the bear to follow her. She said that her name was Saila and she knew of a new and exciting adventure that was waiting for the bear.

The bear accepted the invitation and followed Saila to a secret place deep in the forest. As they went, they saw lots of fascinating things. They even made friends with some of the animals along the way. When they arrived at the secret place, the bear was so happy and excited to start the adventure!

Saila taught the bear lots of new things and together they went on many fun adventures. The bear was so glad that he had resisted the poison because the journey with Saila was much better than it would have been if he ate the treat. The adventures he had helped him to grow and learn in so many ways. The bear was so lucky and grateful for the amazing journey!
```

### 全部目标故事文段（候选外的文段也需检查）

**story_003318_chunk_000**

```text
Once upon a time there was an adventurous bear. One day, the bear was walking through the forest when he came across a yummy treat. The treat looked tasty and the bear wanted to eat it. But then he realized that it was poison! The bear resisted the temptation to eat it.

The bear then heard a voice calling him. He looked up and saw a beautiful bird in a nearby tree. The bird asked the bear to follow her. She said that her name was Saila and she knew of a new and exciting adventure that was waiting for the bear.

The bear accepted the invitation and followed Saila to a secret place deep in
```

**story_003318_chunk_001**

```text
a and she knew of a new and exciting adventure that was waiting for the bear.

The bear accepted the invitation and followed Saila to a secret place deep in the forest. As they went, they saw lots of fascinating things. They even made friends with some of the animals along the way. When they arrived at the secret place, the bear was so happy and excited to start the adventure!

Saila taught the bear lots of new things and together they went on many fun adventures. The bear was so glad that he had resisted the poison because the journey with Saila was much better than it would have been if he ate the treat
```

**story_003318_chunk_002**

```text
 adventures. The bear was so glad that he had resisted the poison because the journey with Saila was much better than it would have been if he ate the treat. The adventures he had helped him to grow and learn in so many ways. The bear was so lucky and grateful for the amazing journey!
```


## q030

问题：What appeared in the sky and brought water to the angry man who could not find any?

预期答案：A big white cloud.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once there was a bad man who wanted some water. He looked everywhere but he couldn't find any water. He was so angry he started to cry.

Then something special happened. A big white cloud appeared in the sky and filled the air with water. The water floated down from the sky and wrapped the bad man in a big hug. The water was so soft and comforting.

The bad man felt happy. He smiled for the first time in days. He jumped in the water and soaked up the sun. He swam in the water for hours and felt so clean and refreshed.

The bad man thanked the cloud for bringing the water and wrapped himself up in a big, warm towel. He no longer felt bad and went on his way feeling happy and refreshed.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_003461_chunk_000**

```text
Once there was a bad man who wanted some water. He looked everywhere but he couldn't find any water. He was so angry he started to cry.

Then something special happened. A big white cloud appeared in the sky and filled the air with water. The water floated down from the sky and wrapped the bad man in a big hug. The water was so soft and comforting.

The bad man felt happy. He smiled for the first time in days. He jumped in the water and soaked up the sun. He swam in the water for hours and felt so clean and refreshed.

The bad man thanked the cloud for bringing the water and
```

**story_003461_chunk_001**

```text
 and soaked up the sun. He swam in the water for hours and felt so clean and refreshed.

The bad man thanked the cloud for bringing the water and wrapped himself up in a big, warm towel. He no longer felt bad and went on his way feeling happy and refreshed.
```


## q031

问题：In Pete's cupboard story, in which direction did the walls and furniture move when the room started to reverse?

预期答案：Backwards.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a little boy named Pete. Pete was three years old and he was very curious. 

One day, he saw something interesting in his house: a cupboard. Pete opened the cupboard and saw that it was clean. He saw a big handle and a switch inside the cupboard. 

Pete was curious, so he pulled the handle and pressed the switch. Suddenly, the room started to reverse. The walls and furniture moved backwards. Pete laughed and clapped his hands. 

But then, the reversinng stopped and Pete's mom came in the room. She saw what Pete did and she said, "No no, Pete. You must not play with things inside the cupboard."

Pete felt very sorry. He said sorry to his mom and promised that he would not play with it again.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_003600_chunk_000**

```text
Once upon a time, there was a little boy named Pete. Pete was three years old and he was very curious. 

One day, he saw something interesting in his house: a cupboard. Pete opened the cupboard and saw that it was clean. He saw a big handle and a switch inside the cupboard. 

Pete was curious, so he pulled the handle and pressed the switch. Suddenly, the room started to reverse. The walls and furniture moved backwards. Pete laughed and clapped his hands. 

But then, the reversinng stopped and Pete's mom came in the room. She saw what Pete did and she said,
```

**story_003600_chunk_001**

```text
 clapped his hands. 

But then, the reversinng stopped and Pete's mom came in the room. She saw what Pete did and she said, "No no, Pete. You must not play with things inside the cupboard."

Pete felt very sorry. He said sorry to his mom and promised that he would not play with it again.
```


## q032

问题：What did Nan and Pap decide to build together on their beach vacation?

预期答案：A huge sandcastle.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Nan and Pap were on a huge vacation. Nan took her bucket to the beach, and said to Pap:

"Let's go soak our feet in the ocean."

So, Nan and Pap wiggled their toes in the water. It felt so nice! The water was warm, and the sun was shining. Pap said it was the best vacation ever.

After a while, Nan and Pap decided to sit down. Nan put her bucket into the sand and said:

"Let's make a huge sandcastle!"

So, Nan and Pap worked hard to make the sandcastle. It was almost done when a wave crashed over them, and they had to start all over again.

In the end, Nan and Pap had a huge sandcastle. They put their bucket on top and smiled.

"We did it!" said Nan.

Pap said: "This is the best vacation ever!"
```

### 全部目标故事文段（候选外的文段也需检查）

**story_003730_chunk_000**

```text
Nan and Pap were on a huge vacation. Nan took her bucket to the beach, and said to Pap:

"Let's go soak our feet in the ocean."

So, Nan and Pap wiggled their toes in the water. It felt so nice! The water was warm, and the sun was shining. Pap said it was the best vacation ever.

After a while, Nan and Pap decided to sit down. Nan put her bucket into the sand and said:

"Let's make a huge sandcastle!"

So, Nan and Pap worked hard to make the sandcastle. It was almost done when a wave crashed over them,
```

**story_003730_chunk_001**

```text
Let's make a huge sandcastle!"

So, Nan and Pap worked hard to make the sandcastle. It was almost done when a wave crashed over them, and they had to start all over again.

In the end, Nan and Pap had a huge sandcastle. They put their bucket on top and smiled.

"We did it!" said Nan.

Pap said: "This is the best vacation ever!"
```


## q033

问题：Why did Bob have to wait before he could enter the playground?

预期答案：The playground was not open yet.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
The sun was gloomy and it made the day seem so still.

Bob wanted to go outside and play, so he pushed open the door and ran out.

Everything seemed so big and exciting. He saw huge trees and colourful flowers. But then he noticed that the playground wasn't open yet.

Bob was sad and he didn't want to go back inside. But his mom told him he had to wait.

Bob sighed and crossed his arms. He knew he had to wait before he could play.

So he waited and waited, watching the sun until it was time to go in. 

But just before he went inside, he saw the playground open. He smiled and pushed open the gate and ran inside, ready to have fun.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_003851_chunk_000**

```text
The sun was gloomy and it made the day seem so still.

Bob wanted to go outside and play, so he pushed open the door and ran out.

Everything seemed so big and exciting. He saw huge trees and colourful flowers. But then he noticed that the playground wasn't open yet.

Bob was sad and he didn't want to go back inside. But his mom told him he had to wait.

Bob sighed and crossed his arms. He knew he had to wait before he could play.

So he waited and waited, watching the sun until it was time to go in. 

But just before he went inside, he saw the
```

**story_003851_chunk_001**

```text
 he could play.

So he waited and waited, watching the sun until it was time to go in. 

But just before he went inside, he saw the playground open. He smiled and pushed open the gate and ran inside, ready to have fun.
```


## q034

问题：What kind of music did Lily, whose little brother bothered her while she danced in her room, like best?

预期答案：Jazz.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a little girl named Lily. She loved to dance and listen to music. Her favorite kind of music was jazz. She would dance around her room every day to the jazz music.

One day, Lily's little brother came into her room and started to bother her. He was being very naughty and wouldn't stop. Lily got very angry and slapped him on the arm. She felt guilty right away and apologized to her brother.

After they made up, Lily put on some jazz music and they both danced together. They had so much fun and forgot all about their fight. From then on, Lily promised to never slap her brother again and they danced to jazz music together every day.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_003975_chunk_000**

```text
Once upon a time, there was a little girl named Lily. She loved to dance and listen to music. Her favorite kind of music was jazz. She would dance around her room every day to the jazz music.

One day, Lily's little brother came into her room and started to bother her. He was being very naughty and wouldn't stop. Lily got very angry and slapped him on the arm. She felt guilty right away and apologized to her brother.

After they made up, Lily put on some jazz music and they both danced together. They had so much fun and forgot all about their fight. From then on, Lily promised to
```

**story_003975_chunk_001**

```text
, Lily put on some jazz music and they both danced together. They had so much fun and forgot all about their fight. From then on, Lily promised to never slap her brother again and they danced to jazz music together every day.
```


## q035

问题：Where did Sue and the formerly lonely ugly duck meet every day to play?

预期答案：At the pond.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, in a small village, there lived an ugly duck. The duck was sad because no one wanted to play with him. He would sit by the pond and watch the other ducks swim and have fun.

One day, a little girl named Sue came to the pond. She saw the ugly duck and felt bad for him. Sue walked up to the duck and said, "Hi, do you want to play with me?" The ugly duck was surprised and happy. He requested, "Can I have some water to swim in?"

Sue nodded and found a bucket. She filled it with water and poured it into the pond. The ugly duck jumped in and splashed around. They both laughed and played together all day long.

From that day on, the ugly duck and Sue became best friends. They would meet at the pond every day to play and have fun. The other ducks saw how happy the ugly duck was and wanted to join in too. Soon, the ugly duck wasn't lonely anymore, and everyone in the village loved him.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_004119_chunk_000**

```text
Once upon a time, in a small village, there lived an ugly duck. The duck was sad because no one wanted to play with him. He would sit by the pond and watch the other ducks swim and have fun.

One day, a little girl named Sue came to the pond. She saw the ugly duck and felt bad for him. Sue walked up to the duck and said, "Hi, do you want to play with me?" The ugly duck was surprised and happy. He requested, "Can I have some water to swim in?"

Sue nodded and found a bucket. She filled it with water and poured it into the
```

**story_004119_chunk_001**

```text
. He requested, "Can I have some water to swim in?"

Sue nodded and found a bucket. She filled it with water and poured it into the pond. The ugly duck jumped in and splashed around. They both laughed and played together all day long.

From that day on, the ugly duck and Sue became best friends. They would meet at the pond every day to play and have fun. The other ducks saw how happy the ugly duck was and wanted to join in too. Soon, the ugly duck wasn't lonely anymore, and everyone in the village loved him.
```


## q036

问题：What food did Tony choose for dinner before he felt unwell and rushed to the toilet?

预期答案：A small apple, a banana, and some chips.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once there was a small boy called Tony. He was only three years old. His mum and dad said to him one day, "You can choose your own food for dinner tonight, Tony!"

Tony was so excited. He chose a small apple, a banana and some chips. He thought this was the very best food ever. 

However, when Tony ate the food, he started to feel unwell. He felt funny in his tummy and he had to rush to the toilet. His mum and dad said, "Oh, Tony - it was a bad choice for dinner!"

Tony was so sad. His tummy hurt and he had to sit on the toilet for a long time. He realised that sometimes it isn't so fun to choose your own food!
```

### 全部目标故事文段（候选外的文段也需检查）

**story_004256_chunk_000**

```text
Once there was a small boy called Tony. He was only three years old. His mum and dad said to him one day, "You can choose your own food for dinner tonight, Tony!"

Tony was so excited. He chose a small apple, a banana and some chips. He thought this was the very best food ever. 

However, when Tony ate the food, he started to feel unwell. He felt funny in his tummy and he had to rush to the toilet. His mum and dad said, "Oh, Tony - it was a bad choice for dinner!"

Tony was so sad. His tummy hurt and he
```

**story_004256_chunk_001**

```text
 toilet. His mum and dad said, "Oh, Tony - it was a bad choice for dinner!"

Tony was so sad. His tummy hurt and he had to sit on the toilet for a long time. He realised that sometimes it isn't so fun to choose your own food!
```


## q037

问题：Why did Emma and her mother ask the shopkeeper for a little pie instead of the one on the counter?

预期答案：The big round pie was too big for Emma to catch.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a little girl named Emma. She was always excited to go out with her mom to catch yummy treats. 

One day, Emma asked her mom, "Where are we going?" Her mom said, "We are going out to catch something special today. I'm sure you'll like it." 

Emma said, "What is it? Can I help?" Her mom said, "Yes, we're going to catch a pie!" Emma liked the sound of that and was excited to go. 

When they got to the shop, Emma saw a big, round pie sitting on the counter. She wanted to catch it, but it was too big. So they asked the shopkeeper if they could have a little pie. 

The shopkeeper served them a little pie and Emma caught it with her little hands. She was so delighted that she jumped for joy! The little girl and her mom were so happy about catching the pie!
```

### 全部目标故事文段（候选外的文段也需检查）

**story_004378_chunk_000**

```text
Once upon a time, there was a little girl named Emma. She was always excited to go out with her mom to catch yummy treats. 

One day, Emma asked her mom, "Where are we going?" Her mom said, "We are going out to catch something special today. I'm sure you'll like it." 

Emma said, "What is it? Can I help?" Her mom said, "Yes, we're going to catch a pie!" Emma liked the sound of that and was excited to go. 

When they got to the shop, Emma saw a big, round pie sitting on the counter. She wanted
```

**story_004378_chunk_001**

```text
 the sound of that and was excited to go. 

When they got to the shop, Emma saw a big, round pie sitting on the counter. She wanted to catch it, but it was too big. So they asked the shopkeeper if they could have a little pie. 

The shopkeeper served them a little pie and Emma caught it with her little hands. She was so delighted that she jumped for joy! The little girl and her mom were so happy about catching the pie!
```


## q038

问题：Who examined the bird's wing and gave it medicine after the cat took it directly to another animal for help?

预期答案：A wise owl examined its wing and gave it medicine.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a small bird who loved to sing. One day, the bird fell down from the tree and felt a lot of pain in its wing. The bird tried to fly, but it couldn't. It felt sad and scared.

The bird saw a kind cat who came to question it. The bird told the cat about its pain and how it couldn't fly. The cat felt sorry for the bird and wanted to help. The cat took the bird to a wise owl who knew how to heal small birds.

The owl examined the bird's wing and gave it some medicine. After a few days, the bird's wing felt better and it could fly again. The bird was happy and grateful to the cat and the owl. From that day on, the bird sang even more beautifully than before.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_004500_chunk_000**

```text
Once upon a time, there was a small bird who loved to sing. One day, the bird fell down from the tree and felt a lot of pain in its wing. The bird tried to fly, but it couldn't. It felt sad and scared.

The bird saw a kind cat who came to question it. The bird told the cat about its pain and how it couldn't fly. The cat felt sorry for the bird and wanted to help. The cat took the bird to a wise owl who knew how to heal small birds.

The owl examined the bird's wing and gave it some medicine. After a few days, the bird
```

**story_004500_chunk_001**

```text
 to a wise owl who knew how to heal small birds.

The owl examined the bird's wing and gave it some medicine. After a few days, the bird's wing felt better and it could fly again. The bird was happy and grateful to the cat and the owl. From that day on, the bird sang even more beautifully than before.
```


## q039

问题：Where did Jack go to play with his new puppy after hugging his parents?

预期答案：The backyard.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
Once upon a time, there was a smart young boy called Jack. He was always trying to learn new things and his parents were so proud.

One day, Jack saw his mom and dad walking with a new puppy. He asked them, "What's that?". They replied, "It's a little pup! We've decided to spoil you with a puppy for your youth!" 

Jack was so excited! He laughed and hugged his parents, and couldn't wait to show the puppy all of his favourite games. He ran to the backyard and started to play with the puppy.

They spent the whole day running and playing together, and Jack learned many things. He was so happy to have a new best friend. No one could spoil him more than his parents!
```

### 全部目标故事文段（候选外的文段也需检查）

**story_004638_chunk_000**

```text
Once upon a time, there was a smart young boy called Jack. He was always trying to learn new things and his parents were so proud.

One day, Jack saw his mom and dad walking with a new puppy. He asked them, "What's that?". They replied, "It's a little pup! We've decided to spoil you with a puppy for your youth!" 

Jack was so excited! He laughed and hugged his parents, and couldn't wait to show the puppy all of his favourite games. He ran to the backyard and started to play with the puppy.

They spent the whole day running and playing together, and
```

**story_004638_chunk_001**

```text
 the puppy all of his favourite games. He ran to the backyard and started to play with the puppy.

They spent the whole day running and playing together, and Jack learned many things. He was so happy to have a new best friend. No one could spoil him more than his parents!
```


## q040

问题：What caught Sarah's attention while she was walking through the park with her mother?

预期答案：A big tree covered with bright red cherries.

检查：Full answer and question conditions supported?；All sufficient single-chunk IDs included?；Correct target story and exact quote attribution?

### 原始目标故事

```text
One day there was a young girl named Sarah. She was walking through the park with her mum when she saw something that made her stop in her tracks. In the distance, there was a big tree with lots of bright red cherries on it. She pulled on her mothers hand and pointed at the tree, saying that she wanted to get one. 

Her Mother smiled and told her she could, but that they would need to go home first to get a basket. After picking up the basket from their house, they walked back to the park. 

Sarah was very happy. She raced to the tree and stretched her hands up to pick the closest one she could reach. But when she pulled her hand back the cherry was gone, leaving a branch full of empty stems where it had been. 

Sarah was sad. She looked at her mum and asked what had happened. Her mum simply smiled, reached into her pocket, and pulled out the same bright red cherry that Sarah had pointed at earlier.

Sarah was amazed. She asked how her Mum had known where to find the cherry, but her Mum just kept smiling. If Sarah had only realised earlier, she could have had the cherry much sooner!
```

### 全部目标故事文段（候选外的文段也需检查）

**story_004763_chunk_000**

```text
One day there was a young girl named Sarah. She was walking through the park with her mum when she saw something that made her stop in her tracks. In the distance, there was a big tree with lots of bright red cherries on it. She pulled on her mothers hand and pointed at the tree, saying that she wanted to get one. 

Her Mother smiled and told her she could, but that they would need to go home first to get a basket. After picking up the basket from their house, they walked back to the park. 

Sarah was very happy. She raced to the tree and stretched her hands up to pick
```

**story_004763_chunk_001**

```text
 up the basket from their house, they walked back to the park. 

Sarah was very happy. She raced to the tree and stretched her hands up to pick the closest one she could reach. But when she pulled her hand back the cherry was gone, leaving a branch full of empty stems where it had been. 

Sarah was sad. She looked at her mum and asked what had happened. Her mum simply smiled, reached into her pocket, and pulled out the same bright red cherry that Sarah had pointed at earlier.

Sarah was amazed. She asked how her Mum had known where to find the cherry, but her Mum just kept smiling.
```

**story_004763_chunk_002**

```text
 cherry that Sarah had pointed at earlier.

Sarah was amazed. She asked how her Mum had known where to find the cherry, but her Mum just kept smiling. If Sarah had only realised earlier, she could have had the cherry much sooner!
```


## q041

问题：In the story where Lily finds a needle and her mother sews a button on her shirt, what is the exact manufacturer and model number of the needle?

预期答案：The story does not specify the manufacturer or model number of the needle.

检查：Correct complete target story?；Requested information still absent?

### 原始目标故事

```text
One day, a little girl named Lily found a needle in her room. She knew it was difficult to play with it because it was sharp. Lily wanted to share the needle with her mom, so she could sew a button on her shirt.

Lily went to her mom and said, "Mom, I found this needle. Can you share it with me and sew my shirt?" Her mom smiled and said, "Yes, Lily, we can share the needle and fix your shirt."

Together, they shared the needle and sewed the button on Lily's shirt. It was not difficult for them because they were sharing and helping each other. After they finished, Lily thanked her mom for sharing the needle and fixing her shirt. They both felt happy because they had shared and worked together.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_000000_chunk_000**

```text
One day, a little girl named Lily found a needle in her room. She knew it was difficult to play with it because it was sharp. Lily wanted to share the needle with her mom, so she could sew a button on her shirt.

Lily went to her mom and said, "Mom, I found this needle. Can you share it with me and sew my shirt?" Her mom smiled and said, "Yes, Lily, we can share the needle and fix your shirt."

Together, they shared the needle and sewed the button on Lily's shirt. It was not difficult for them because they were sharing and helping each other
```

**story_000000_chunk_001**

```text
 shirt."

Together, they shared the needle and sewed the button on Lily's shirt. It was not difficult for them because they were sharing and helping each other. After they finished, Lily thanked her mom for sharing the needle and fixing her shirt. They both felt happy because they had shared and worked together.
```


## q042

问题：In the story where a cat takes an injured bird to a wise owl, what is the exact medicine name and dose that the owl gives the bird?

预期答案：The story says the owl gives the bird some medicine, but does not specify its name or dose.

检查：Correct complete target story?；Requested information still absent?

### 原始目标故事

```text
Once upon a time, there was a small bird who loved to sing. One day, the bird fell down from the tree and felt a lot of pain in its wing. The bird tried to fly, but it couldn't. It felt sad and scared.

The bird saw a kind cat who came to question it. The bird told the cat about its pain and how it couldn't fly. The cat felt sorry for the bird and wanted to help. The cat took the bird to a wise owl who knew how to heal small birds.

The owl examined the bird's wing and gave it some medicine. After a few days, the bird's wing felt better and it could fly again. The bird was happy and grateful to the cat and the owl. From that day on, the bird sang even more beautifully than before.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_004500_chunk_000**

```text
Once upon a time, there was a small bird who loved to sing. One day, the bird fell down from the tree and felt a lot of pain in its wing. The bird tried to fly, but it couldn't. It felt sad and scared.

The bird saw a kind cat who came to question it. The bird told the cat about its pain and how it couldn't fly. The cat felt sorry for the bird and wanted to help. The cat took the bird to a wise owl who knew how to heal small birds.

The owl examined the bird's wing and gave it some medicine. After a few days, the bird
```

**story_004500_chunk_001**

```text
 to a wise owl who knew how to heal small birds.

The owl examined the bird's wing and gave it some medicine. After a few days, the bird's wing felt better and it could fly again. The bird was happy and grateful to the cat and the owl. From that day on, the bird sang even more beautifully than before.
```


## q043

问题：In the story about the wealthy family whose youngest child is three years old and visits university, what is the official street address of that university?

预期答案：The story does not give the university's street address.

检查：Correct complete target story?；Requested information still absent?

### 原始目标故事

```text
Once there was a wealthy family with three kids. Two of them were in university, but the youngest one was only three. He wanted to go to university too!

One day, the three university students decided to take the youngest one with them on a fun day out. As they drove to the university, the little kid cheered with joy. 

When they arrived, the little kid wanted to explore everywhere. He ran around and screamed with excitement!

The university students showed him all the places and got him some ice cream. He was having so much fun!

At the end of the day, the family drove home and the little kid felt so happy. He dreamed of one day going to university too.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_001662_chunk_000**

```text
Once there was a wealthy family with three kids. Two of them were in university, but the youngest one was only three. He wanted to go to university too!

One day, the three university students decided to take the youngest one with them on a fun day out. As they drove to the university, the little kid cheered with joy. 

When they arrived, the little kid wanted to explore everywhere. He ran around and screamed with excitement!

The university students showed him all the places and got him some ice cream. He was having so much fun!

At the end of the day, the family drove home and the little kid felt so
```

**story_001662_chunk_001**

```text
 places and got him some ice cream. He was having so much fun!

At the end of the day, the family drove home and the little kid felt so happy. He dreamed of one day going to university too.
```


## q044

问题：In the story where Timmy and Billy play a drum together every day, what is the manufacturer and model number of that drum?

预期答案：The story does not specify the manufacturer or model number of the drum.

检查：Correct complete target story?；Requested information still absent?

### 原始目标故事

```text
Once upon a time, there was a boy named Timmy. Timmy loved to play with his huge drum. He would bang on it all day long and laugh when he made loud noises. 

One day, Timmy's friend Billy came over to play. Billy saw Timmy's drum and said, "Wow, that's a big drum!" Timmy said, "Yes, it's huge! Do you want to play with it?" 

Billy nodded his head and started to bang on the drum. Timmy laughed and said, "You're really good at playing the drum, Billy!" Billy smiled and said, "Thanks, Timmy. I like playing with your drum." 

From that day on, Timmy and Billy played together every day. They would bang on the drum and laugh together. They were the best of friends and they loved playing music together. The end.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_002365_chunk_000**

```text
Once upon a time, there was a boy named Timmy. Timmy loved to play with his huge drum. He would bang on it all day long and laugh when he made loud noises. 

One day, Timmy's friend Billy came over to play. Billy saw Timmy's drum and said, "Wow, that's a big drum!" Timmy said, "Yes, it's huge! Do you want to play with it?" 

Billy nodded his head and started to bang on the drum. Timmy laughed and said, "You're really good at playing the drum, Billy!" Billy smiled and said, "Thanks
```

**story_002365_chunk_001**

```text
 started to bang on the drum. Timmy laughed and said, "You're really good at playing the drum, Billy!" Billy smiled and said, "Thanks, Timmy. I like playing with your drum." 

From that day on, Timmy and Billy played together every day. They would bang on the drum and laugh together. They were the best of friends and they loved playing music together. The end.
```


## q045

问题：In the story where Jack asks Jill to help him make something special using clay, how many grams of clay do they use?

预期答案：The story does not specify how many grams of clay they use.

检查：Correct complete target story?；Requested information still absent?

### 原始目标故事

```text
Once upon a time, there were two friends: Jack and Jill. Jack had a brilliant idea. He wanted to make something special using clay.

He asked Jill for help to match the pieces of clay together. She was happy to join in and the two began to make something exciting.

With Jill's help, shapes and designs began to appear from the clay. Hours passed, and eventually the friends had made something really fantastic. It was a beautiful clay castle.

They stood back to admire their work. Jill said it was brilliant, and Jack was very proud.

The castle was the perfect match for their creativity! They both knew it was something special. The end.
```

### 全部目标故事文段（候选外的文段也需检查）

**story_001097_chunk_000**

```text
Once upon a time, there were two friends: Jack and Jill. Jack had a brilliant idea. He wanted to make something special using clay.

He asked Jill for help to match the pieces of clay together. She was happy to join in and the two began to make something exciting.

With Jill's help, shapes and designs began to appear from the clay. Hours passed, and eventually the friends had made something really fantastic. It was a beautiful clay castle.

They stood back to admire their work. Jill said it was brilliant, and Jack was very proud.

The castle was the perfect match for their creativity! They both knew it was something
```

**story_001097_chunk_001**

```text
 admire their work. Jill said it was brilliant, and Jack was very proud.

The castle was the perfect match for their creativity! They both knew it was something special. The end.
```
