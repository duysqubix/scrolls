class Disease:
    __obj_name__ = ""
    pass


class Ataxia(Disease):
    """
    Ataxia is a commona and relatively mild disease found across
    the breadth of Tamriel. Its symptoms include general pain and
    soreness, muscle stiffness, and anemia. Victims of Ataxia are
    often pale, groggy, and irritable. Some particularly devious
    bandits and trap-makers are known to spring vials or lace nails
    with the bodily fluids of dead animals that carry the disease.

    Symptoms
    --------
    Loss of Agility and Strength affecting Subterfuge and Block 
    abilities.

    Carriers
    --------
    Cave Rats; Bears; Alit; Giant Spiders; Slaughterfish; Zombies;
    Traps

    Prognosis
    ---------
    Symptoms are mild for one week. If not cured they can increase
    in severity any time after seven days. 
    """
    __obj_name__ = "ataxia"
    pass


class BrainRot(Disease):
    """
    Brain Rot is a progressively worsening, mind affecting disease.
    It dampens the intelligence, intuition, and mental acuity of its
    victims. Eventually, Brain Rot destroys any semblance of sanity
    and of the self in its victims, leaving them to shuffle in a broken
    stupor until they are cured or die.

    Symptoms
    --------
    Loss of Magicka, Intelligence, and Personality, in that order as 
    the disease progresses.

    Carriers
    --------
    Cave Rats; Zombies; Hagravens; Traps

    Prognosis
    ---------
    Loss of Magicka starts immediately after infection. After one week
    there is a chance that Intelligence will be affected as well. If 
    that occurs then after a further week it is possible to suffer the
    loss of Personality as well, unless cured.
    """
    __obj_name__ = "brain rot"
    pass


class BoneBreak(Disease):
    """
    Bone Break Fever is particularly cruel disease. Carried primarily
    by rats and bears, the disease aggressively attacks the victim's
    bones until they are vulnerable and pront to breakage. Untreated
    Bone Break Fever often results in crippled, or outtright severed
    limbs because of the fragility it causes in its victims.

    Symptoms
    --------
    Loss of strength and endurance in the early stages, progressing to
    weakness to Shock at the later stage.

    Carriers
    --------
    Cave Rats; Bears; Wolves

    Prognosis
    ---------
    After a three day incubation period, early stage symptoms appear. 
    After a week late stage may develop.
    """
    __obj_name__ = "bone break fever"
    pass


class BloodLung(Disease):
    """
    A relatively minor, non life-threatening illness, Blood Lung
    causes bleeding cysts in the victim's lungs. They are prone to
    rupture at inconvenient times or times of physical exertion.
    While Blood Lung is not severem and will not typically worsen, it
    does open the door for other diseases to take root, and can also
    server as a vector for others via the coughed up blood.

    Symptoms
    --------
    Loss of endurance, increase in fatigue, and 
    << every SP used after inflicts 1d4 of damage ignoring armour>>

    Carriers
    --------
    Cave Rats; Nix-Hounds

    Prognosis
    ---------
    Symptoms take effect after a three day incubation stage and persist 
    unil cured.
    """
    __obj_name__ = "blood lung"
    pass


class  BlackHeart(Disease):
    """
    Black Heart Blight, despite being a member of the Blight family
    of diseases created by Dagoth Ur, is both a blight and a 
    common disease and is less severe than its cousins. After the
    ending of the Blight in 3E 427, Black Heart Blight survived after
    making the jump to undead. It is carried by zombies exclusively
    after the destruction of Dagoth Ur, but prior to his death it was
    also carried by the various blighted beasts or Corprus monsters
    of Morrowind. It is an acute disease that saps the victim's vitality
    and endurance.

    Symptoms
    --------
    Initial loss of endurance; followed by loss of carrying capacity in
    late stage.

    Carriers
    --------
    Zombies

    Prognosis
    ---------
    Symptoms occur imediately after infection and worsen (enter late stage)
    after three days.
    """
    __obj_name__ = "black heart blight"
    pass


class  Chills(Disease):
    """
    The Chills are a punishing infection caused by contact with the
    undead. It affects the victim's mind and motor skills equally,
    resulting in confused, inarticulate stupors. Its other symptoms
    include an overwhelming sensation of cold that is not affected
    by the warmth of any fire, nor the light of the sun. It has lead
    to the death of many an unfortuneate adventurer, lost, alone, 
    and cold in the crypts that dot Tamriel.

    Symptoms
    --------
    Loss of intelligence, willpower, and agility and general impairment
    to all mental and motor skills.

    Carriers
    --------
    Zombies; Bonelord; Bonewalker

    Prognosis
    ---------
    The disease incubated for only one hour, then suddenly overcomes 
    the victim and all symptoms occur at once.
    """
    __obj_name__ = "chills"
    pass


class  Collywobbles(Disease):
    """
    Collywobbles' main symptoms are uncontrollable shaking and 
    chronic ache. The constant minor shaking and spasming can
    become debilitating, and the strain of the shakes causes muscle
    soreness.

    Symptoms
    --------
    Inital impairment to agility and endurance; followed by worsenning
    symptoms and <<reduce max ap>>.

    Carriers
    --------
    Zombies; Shalks

    Prognosis
    ---------
    Secondary symptoms may start occuring anytime after the first week.
    """
    __obj_name__ = "collywobbles"
    pass


class  Dampworm(Disease):
    """
    Dampworm is a parasite that infests the victim's musculature,
    slithering in between the tissue. It can be felt occasionlly
    moving underneath the skin, which is a revolting and disturbing
    experience to say the least. Its symptoms include minor twitches
    and lapses in gross motor skill, as well as uncontrollable sweating.

    Symptoms
    --------
    Reduction in the host's speed.

    Carriers
    --------
    Nix-Hounds; Deer; Horses; Falmer

    Prognosis
    ---------
    Dampworm symptoms remain stable over time.
    """
    __obj_name__ = "dampworm"
    pass


class  Droops(Disease):
    """
    The Droops are a notorious and serious common disease that
    result in weakened and exhausted muscles. They result in 
    excessive fatigue after virtually any physical exertion.

    Symptoms
    --------
    Loss of strength, loss of stamina.

    Carriers
    --------
    Zombies; Sheep; Kwama

    Prognosis
    ---------
    Symptoms remain stable over time. 
    """
    __obj_name__ = "the droops"
    pass


class  Frostlimb(Disease):
    """
    A relatively obscure disease, Frostlimb causes intense sensations
    of coldness within the victim's arms and legs, and especially their
    fingers. As a result, fine motor skills are punished greatly, and
    the effects of Frost damage is greatly magnified.

    Symptoms
    --------
    Weakness to Frost; impairment of all fine motor skills.

    Carriers
    --------
    Trolls, Mammoths, Falmer

    Prognosis
    ---------
    Symptoms remain stable over time.
    """
    __obj_name__ = "frostlimb"
    pass


class  Greenspore(Disease):
    """
    Carried primarily by slaughterfish, Greenspore is a mind affecting
    fungus that causes irritability and mild dementia. The spores
    take root in the victim's mind, but are easily treated in the early
    stages. Mature Greenspore can cause permanent brain damage.

    Symptoms
    --------
    At onset loss of peronality which progressively worsens in late stages.

    Carriers
    --------
    Slaugherfish; Zombies

    Prognosis
    ---------
    After a week personality damage may begin to deteriorate very rapidly.
    """
    __obj_name__ = "greenspore"
    pass


class  Helljoint(Disease):
    """
    Helljoint is a mild, inflammatory disease that causes swelling
    of the joints and mild irritating pain. It is extremely common 
    in Northern climes, and is easily contracted and cured.

    Symptoms
    --------
    Imediately damages the victim's agility and inhibits the ability to run
    and sprint.

    Carriers
    --------
    Zombies; Cliff Racers; Wolves

    Prognosis
    ---------
    Symptoms remain stable over time.
    """
    __obj_name__ = "helljoint"
    pass


class  Rattles(Disease):
    """
    The Rattles is a mild disease of subtle nervous ticks. The Rattles
    cause light finger ticks and forgetfulness. Victims of the Rattles
    are reported as appearing restless to the point of irritation,
    though the sufferers of the disease aren't aware of their ticks
    unless paying deliberate attention.

    Symptoms
    --------
    Losse of agility and willpower.

    Carriers
    --------
    Cave Rats; Nix-Hounds; Chaurus; Zombies; Skeletons

    Prognosis
    ---------
    Symptoms remain stable over time.
    """
    __obj_name__ = "the rattles"
    pass


class  RedFever(Disease):
    """
    A notorious and common illness, Red Fever often hits during
    late autumn, or through contact with wild wolves or dogs. The
    fever is short lived but intense, causing intense sweating, fever,
    vomiting, and often other unpleasant bodily functions. Red
    Fever is known to put even the mightiest warrior into fits of
    anguish for its brief, but hellish duration.

    Symptoms
    --------
    Chance to become utterly debilitated for a 24 hour period. 

    Carriers
    --------
    Wolves, Dogs, Cave Rats

    Prognosis
    ---------
    Incubates for one day, then accute phase lasts for three days after
    which the disease "cures" itself.
    """
    __obj_name__ = "red fever"
    pass


class  Rockjoint(Disease):
    """
    Rockjoint is a pervasive and ubiquitous disease across Tamriel.
    Every adventurer, noble lord, or peasant farmer has either had
    Rockjoint, or has personally known someone with Rockjoing.
    Rockjoint swells the knees and elbows with sensitive and painful
    fluids that bloat and then stiffen, and can lead to total
    immobility if left unchecked.

    Symptoms
    --------
    In the early stages Rockjoint impairs strength and agility and
    as it progresses these impairments scale up dramatically. In 
    its final stage, Rockjoint completely immobilizes its victim.

    Carriers
    --------
    Guar; Alit; Wolves; Cave Rats; Bears; Horkers; Foxes; Traps;
    Zombies

    Prognosis
    ---------
    After one week it becomes possible to advance to more serious
    stages which will last a mimimum of another week before it 
    becomes possible to reach the final stage.
    """
    __obj_name__ = "rockjoint"
    pass


class  RustChancre(Disease):
    """
    Rust Chancre is a mild disease that affects the victim's skin.
    Blistering, itchy rashes break out in random patches across
    the victim's body, often including their face and neck. The
    crackled rashes are quite off-putting to others, and irritating
    to the sufferer, but ultimately it is not a threatening disease.
    Rust Chancre often leaves permanent scarring after it is cured.

    Symptoms
    --------
    Slight reduction in willpower and disfigurement. 

    Carriers
    --------
    Cave Rats; Zombies; Traps

    Prognosis
    ---------
    Rust Chancre symptoms remain stable, though breakouts may come and
    go. After being cured, the disease leaves permanent ugly scars.
    """
    __obj_name__ = "rust chancre"
    pass


class Shakes(Disease):
    """
    The Shakes are a mild diseases contracted from rats. It is 
    comparable to a much less severe form of the Rattles, that affect the
    entire body rather than just the fingers and face.

    Symptoms
    --------
    Impaired agility.

    Carriers
    --------
    Cave Rats

    Prognosis
    ---------
    Symptoms remain stable until cured.
    """
    __obj_name___ =  "shakes"
    pass


class SwampFever(Disease):
    """
    Swamp Fever is a mild disease carried typically by mudcrabs and
    other aquatic and amphibious vermin. Swamp Fever causes a 
    high body temperature and cold sweats, and is highly contagious,
    but largely non-threatening. The Bitter Coast of Morrowind is
    notorious for extremely high rates of Swamp Fever.

    Symptoms
    --------
    Moderate impairment of strength and endurance; high liklihood
    of infecting others in close contact <<Diseased -30>>

    Carriers
    --------
    Mudcrabs; Cave Rats; Slaugherfish; Crocodiles; Dreugh;
    Giant Snakes

    Prognosis
    ---------
    After one week, the Swamp Fever subsides.
    """
    __obj_name___ =  "swamp fever"
    pass


class TunnelCough(Disease):
    """
    Tunnel Cough is a largely benign disease that affects mostly
    miners and other cave divers and dungeon dwellers. It is characterized
    by dry, hiccup-like coughs. The coughs are not painful or 
    debilitating, but are certainly an inconvenience.

    Symptoms
    --------
    The chronic coughing impairs all stealthy maneuvers.

    Carriers
    --------
    Caused by exposure to ore dust.

    Prognosis
    ---------
    Symptoms remain stable until cured.
    """
    __obj_name___ =  "tunnel cough"
    pass


class Shakes(Disease):
    """
    """
    __obj_name___ =  "shakes"
    pass

ALL_DISEASES = (Ataxia(), BrainRot(), BoneBreak(),  )
