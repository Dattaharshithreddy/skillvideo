import json
P = [
 ("open", "326 BC. Alexander the Great had already crushed the mighty Persian Empire. Now he stood at the gates of India. One by one, the kings in his path bowed… all except one. Purushottam. The Greeks called him Porus.", ["326", "BC.", "Porus."]),
 ("ambhi", "But the first blow against Porus did not come from a foreigner… it came from his own neighbour. Ambhi, the king of Taxila. Out of an old hatred for Porus, he opened his gates to Alexander, and joined hands with the enemy.", ["neighbour.", "Ambhi,", "enemy."]),
 ("river", "With Ambhi's help, Alexander reached the banks of the Jhelum. On the far side waited the army of Porus. By the Greeks' own count… two hundred war elephants. Horses panic at the very sight of them. Crossing head-on was impossible.", ["Jhelum.", "elephants.", "impossible."]),
 ("feint", "So Alexander turned to deception. Night after night, he sent his cavalry racing up and down the bank. Shouting, trumpets, torches… as if the attack had begun. Every time, Porus's army rose and stood ready. Until finally… exhausted, they stopped reacting.", ["deception.", "torches…", "exhausted,"]),
 ("storm", "That was the moment Alexander had been waiting for. One night… thunder, lightning, pouring rain. Under the cover of that storm, he marched upstream, and secretly crossed the river.", ["storm,", "secretly"]),
 ("battle", "By dawn, the enemy was standing on Porus's side of the river. Still, Porus did not retreat. He sent his elephants forward. On one side, elephants like moving hills. On the other, the long Macedonian pikes. It became one of the hardest battles Alexander ever fought.", ["retreat.", "elephants", "hardest"]),
 ("king", "Wounded all over… Porus fought to the very end. He was brought before Alexander as a prisoner. How shall I treat you, Alexander asked. Porus raised his head and said just one thing… As a king treats a king.", ["Wounded", "king", "king."]),
 ("return", "Alexander was so moved that he gave Porus his kingdom back… and made it even larger. Soon after, Alexander's weary army refused to march any deeper into India.", ["kingdom", "refused"]),
 ("murder", "But the story did not end there. After Alexander died, his general Eudemus… plotted against Porus, and had him killed.", ["Eudemus…", "killed."]),
 ("legacy", "Betrayed by a neighbour. Deceived in the dark. Killed by a conspiracy. Yet history remembers Porus in just one word… a king.", ["Betrayed", "king."]),
]
lines = [{"shot": s, "text": t, "tts": t, "keywords": k, "audio": f"audio/p{i+1:02d}.wav"} for i, (s, t, k) in enumerate(P)]
json.dump({"gap": 0.15, "lang": "en", "lines": lines}, open('brief/plan.json', 'w'), indent=1, ensure_ascii=False)
print(len(lines))
