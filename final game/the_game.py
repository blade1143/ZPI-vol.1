import datetime
import os
import glob
import numpy as np
import pygame
import time
import pandas as pd
from tkinter import *
import math


# trzeba zainstalowac xlsxwriter
# trzeba zainstalowac xlwt
# chyba trzeba tez zainstanowac xlrd


def runtest(filename, CycleNo, MinimumBlocks, MaximumBlocks, ProbRew):
    """Główna funckja, odpowiada za przebieg gry."""
    global Stimulus
    global RewardHappy
    global RewardSad

    TrainingCycleLength = 3

    # tworzenie folderów
    current_directory = os.getcwd()
    folder_learning_name = 'learning'
    folder_testing_name = 'testing'

    data_badania = datetime.datetime.now()
    folder_person_name = str(data_badania.year) + '_' + str(data_badania.month) + '_' + str(
        data_badania.day) + '_' + filename

    # folder z wynikami każdej osoby
    person_directory = os.path.join(current_directory, folder_person_name)
    if not os.path.exists(person_directory):
        os.makedirs(person_directory)

    # folder ze zbiorczymi wynikami 'learning'
    learning_directory = os.path.join(current_directory, folder_learning_name)
    if not os.path.exists(learning_directory):
        os.makedirs(learning_directory)

    # folder ze zbiorczymi wynikami 'testing'
    testing_directory = os.path.join(current_directory, folder_testing_name)
    if not os.path.exists(testing_directory):
        os.makedirs(testing_directory)

    # do zapisywania plików 'learning' i 'testing'
    learning_path = learning_directory + "\\" + filename + 'learning.xls'
    testing_path = testing_directory + "\\" + filename + 'testing.xls'
    person_learning_path = person_directory + "\\" + filename + 'learning.xls'
    person_testing_path = person_directory + "\\" + filename + 'testing.xls'

    try:
        stimuli_read = pd.read_excel('stimuli.xls')
        Stimulus = list(stimuli_read['Stimulus values'].values)
    except IOError:
        retval = os.getcwd()  # katalog bieżący
        listing = []
        os.chdir(retval)
        [listing.append(file) for file in glob.glob('o_*.png')]

        Nobrazki = len(listing)
        indices = list(np.random.permutation(listing))
        indices = indices[0:6]
        idxfood = 0

        for index, value in enumerate(indices):
            if str(value) == 'o_food.png':
                idxfood = index

        ind = np.arange(Nobrazki + 2)
        Stimulus = [0] * len(ind)
        Stimulus[0] = str(indices[0])
        Stimulus[1] = str(indices[1])
        Stimulus[2] = str(indices[2])
        Stimulus[3] = str(indices[3])
        Stimulus[4] = str(indices[4])
        Stimulus[5] = str(indices[5])
        pom = Stimulus[5]
        Stimulus[5] = Stimulus[idxfood]
        Stimulus[idxfood] = pom

        retval = os.getcwd()
        listing = []
        os.chdir(retval)
        [listing.append(file) for file in glob.glob('t_*.png')]

        Stimulus[6] = str(listing[0])
        Stimulus[7] = str(listing[1])
        stimuli_df = pd.DataFrame(Stimulus, columns=['Stimulus values'])
        stimuli_writer = pd.ExcelWriter('stimuli.xls', engine='xlwt')
        stimuli_df.to_excel(stimuli_writer)
        stimuli_writer.save()
        stimuli_read = pd.read_excel('stimuli.xls')
        Stimulus = list(stimuli_read['Stimulus values'].values)

    RewardHappy = pygame.image.load('r_happy.png')
    RewardSad = pygame.image.load('r_sad.png')

    # inicjowanie PyGame
    pygame.init()
    clock = pygame.time.Clock()
    clock.tick(60)
    display_info = pygame.display.Info()
    w = display_info.current_w
    h = display_info.current_h
    window_size = (w, h)
    white = (255, 255, 255)
    black = (0, 0, 0)
    red = (255, 0, 0)
    green = (0, 225, 0)
    # # jeśli bez pełnego ekranu
    # screen = pygame.display.set_mode(window_size)
    screen = pygame.display.set_mode(window_size, pygame.FULLSCREEN)
    font_size = round((h / 30) + 5, 0)
    font = pygame.font.SysFont('Arial', int(font_size))

    def addText(text, color, pos):
        text_width, text_height = font.size(text)
        screen.blit(font.render(text, True, color), ((w - text_width) / 2, text_height * pos))

    instruction = [
        # 0
        ['Zapoznaj się z poniższą instrukcją.',
         'Na ekranie będą prezentowane pary różnych obrazków.',
         'Twoim zadaniem jest wybranie jednej z dwóch ilustracji.',
         'Wskazanie "szczęśliwego" obrazka daje większą szansę na nagrodę:',
         'WESOŁA BUŹKA',
         'W przeciwnym przypadku pojawi się kara:',
         'SMUTNA BUŹKA',
         'Twoim celem jest zebranie jak największej liczby nagród.',
         'Naciśnij spację, aby kontynuować.'],
        # 1
        ['Szczęśliwy obrazek wskażesz następującymi klawiszami:',
         '"1" - wybór obrazka po lewej stronie,',
         '"0" - wybór obrazka po prawej stronie.',
         'Wyboru należy dokonywać jak najszybciej (w ciągu 3 sekund).',
         'Naciśnij spację, aby kontynuować.'],
        # 2
        ['Zbierz jak najwięcej nagród oceniając kolejne prezentowane obrazki.',
         'Naciśnij spację, aby kontynuować.'],
        # 3
        ['Zanim zaczniemy badanie,',
         'sprawdzimy czy właściwie rozumiesz podane instrukcje.',
         'Naciśnij spację, aby kontynuować.'],
        # 4
        ['Jakim klawiszem wybiera się obrazek z lewej strony?',
         'Udziel odpowiedzi, wciskając odpowiedni klawisz...'],
        # 5
        ['Jakim klawiszem wybiera się obrazek z prawej strony?',
         'Udziel odpowiedzi, wciskając odpowiedni klawisz...'],
        # 6
        ['Świetnie! Niebawem przejdziemy do właściwego badania.',
         'Przed prezentacją każdej pary obrazków zobaczysz planszę z zieloną kropką.',
         'Połóż ręce na klawiaturze w taki sposób, aby dało się swobodnie naciskać klawisze "1" i "0".',
         'Naciśnij spację, aby kontynuować.'],
        # 7
        ['Na początek kilka par obrazków na próbę.',
         'Naciśnij spację, aby kontynuować.'],
        # 8
        ['Świetnie!',
         'Teraz rozpocznie się właściwa część badania.',
         'Tak jak do tej pory:',
         '"1" - wybór obrazka po lewej stronie,',
         '"0" - wybór obrazka po prawej stronie.',
         'Naciśnij spację, aby kontynuować.'],
        # 9
        ['Spora część badania została wykonana',
         'Jeżeli potrzebujesz przerwy, to jest właśnie ten moment',
         'Naciśnij spację, aby kontynuować.'],
        # 10
        ['Pierwsza część badania za tobą.',
         'W tej chwili zapisywany jest raport z jej przebiegu.'],
        # 11
        ['Zakończono zapisywanie raportu z pierwszej części badania.',
         'Teraz przejdziesz do drugiej części gry.',
         'Jest ona zdecydowanie krótsza od pierwszej części.',
         'Jeśli potrzebujesz, możesz zrobić sobie chwilę przerwy.',
         'Naciśnij spację, aby kontynuować.'],
        # 12
        ['W tej części badania nie będą się pojawiały nagrody ani kary.',
         'Wybieraj te obrazki, które dotychczas były dla ciebie bardziej "szczęśliwe".',
         'Naciśnij spację, aby kontynuować.'],
        # 13
        ['Wszystkie obrazki pojawiały się w poprzedniej części badania,',
         'ale tym razem mogą być zestawione w parach, których wczesniej nie było.',
         'Wybierz wówczas ten obrazek, który wydaje ci się lepszy.',
         'Jeśli nie masz pewności, który obrazek wybrać, zaufaj swojej intuicji.',
         'Naciśnij spację, aby kontynuować.'],
        # 14
        ['Przygotuj się!'],
        # 15
        ['Dziękujemy za dotychczasowy wysiłek. Już prawie jesteśmy przy końcu badania.',
         'Zostało tylko ostatnie krótkie zadanie.',
         'Na następnych planszach pojawią się kolejno wszystkie obrazki.',
         'Przy każdym z nich, wyobraź sobie, że wybierasz go 100 razy pod rząd.',
         'Jak czujesz, ile wówczas nagród (mniej więcej) można za niego otrzymać?',
         'Pod obrazkiem znajdują się 3 buźki. Smutna - zawsze pechowy',
         'Wesoła - zawsze szczęśliwy.',
         'Naciśnij spację, aby kontynuować.'],
        # 16
        ['Gratulacje! Całe badanie zostało ukończone!',
         'Dziękujemy za jego wykonanie.',
         'W tej chwili zapisywany jest raport końcowy...'],
        # 17
        ['Dziękujemy za poświęcony czas.'],
        # 18
        ['Autorzy:',
         'Katarzyna Szymańska',
         'Patryk Janiewski',
         'Patrycja Palus',
         'Patryk Kędzior'],
    ]

    def text_all(instruction, color, pos):
        screen.fill(white)
        pos = pos
        for text in instruction:
            if text == 'WESOŁA BUŹKA':
                addText(text, green, pos)
            elif text == 'SMUTNA BUŹKA':
                addText(text, red, pos)
            else:
                addText(text, color, pos)
            pos += (h / w) * 2.5
        return pygame.display.flip()

    def showfocuspoint(minTime, maxTime):
        radius = 20
        kropka = pygame.Surface([radius, radius], pygame.SRCALPHA, 32).convert_alpha()
        pygame.draw.ellipse(kropka, green, [0, 0, radius, radius])
        kropka_rect = kropka.get_rect()
        kropka_rect.x = w / 2 - radius / 2
        kropka_rect.y = h / 2 - radius / 2
        x = (maxTime - minTime) * np.random.rand() + minTime
        screen.blit(kropka, kropka_rect)
        pygame.display.flip()
        y = (round(x + 0.5, 0)) * 1000
        pygame.time.wait(int(y))

    def elapsed_time(all_time):
        t = time.time()
        elapsed = 0
        while elapsed < all_time:
            elapsed = time.time() - t
        return elapsed

    def getAnyKey():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return pygame.K_SPACE
                if event.key == pygame.K_0:
                    return pygame.K_0
                if event.key == pygame.K_1:
                    return pygame.K_1
                else:
                    return event.key

    def getkeywait(m):
        t = time.time()
        elapsed = 0
        while elapsed < m:
            elapsed = time.time() - t
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_0:
                        return pygame.K_0
                    elif event.key == pygame.K_1:
                        return pygame.K_1
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        screen.fill(white)
        pygame.display.flip()

    def getkeywaitTimer(m):
        t = time.time()
        elapsed = 0
        while elapsed < 0.25 and (getAnyKey() != pygame.K_0 or pygame.K_1):
            elapsed = time.time() - t
        keyOK = False
        while keyOK == False:
            b = getkeywait(m)
            if b == pygame.K_0 or b == pygame.K_1:
                keyOK = True
                if keyOK == False:
                    b = -1
            return b

    def showtrial(LeftStimulusNo, RightStimulusNo, RewardsGranted, tmode):
        global Stimulus
        global RewardHappy
        global RewardSad
        wRewardSad = pygame.Surface.get_width(RewardSad)
        hRewardSad = pygame.Surface.get_height(RewardSad)
        wRewardHappy = pygame.Surface.get_width(RewardHappy)
        hRewardHappy = pygame.Surface.get_height(RewardHappy)
        MaxResponseTime = int(3)
        FeedbackPresentationTime = int(2.5)

        screen.fill(white)
        pygame.display.flip()

        if np.random.randint(2) == 0:
            LStimulusNo = LeftStimulusNo
            RStimulusNo = RightStimulusNo
            if (tmode == 'Feedback'):
                # showtrial(6, 7, [1, 0], 'Feedback')
                LRewardGranted = RewardsGranted[0]
                RRewardGranted = RewardsGranted[1]
                BetterStimulus = pygame.K_1
        else:
            LStimulusNo = RightStimulusNo
            RStimulusNo = LeftStimulusNo
            if (tmode == 'Feedback'):
                LRewardGranted = RewardsGranted[1]
                RRewardGranted = RewardsGranted[0]
                BetterStimulus = pygame.K_0

        # lewy Stimulus
        imL = pygame.image.load(Stimulus[LStimulusNo])
        imLTransform = pygame.transform.scale(imL, (math.floor(h / 2), math.floor(h / 2)))
        wol = pygame.Surface.get_width(imLTransform)
        hol = pygame.Surface.get_height(imLTransform)
        screen.blit(imLTransform, (w / 4 - wol / 2, h / 2 - hol / 2))

        # prawy Stimulus
        imR = pygame.image.load(Stimulus[RStimulusNo])
        imRTransform = pygame.transform.scale(imR, (math.floor(h / 2), math.floor(h / 2)))
        wor = pygame.Surface.get_width(imRTransform)
        hor = pygame.Surface.get_height(imRTransform)
        screen.blit(imRTransform, (3 * w / 4 - wor / 2, h / 2 - hor / 2))

        pygame.display.flip()

        # nagrody
        a = time.time()
        Action = (getkeywaitTimer(MaxResponseTime))
        RTime = time.time() - a
        if (tmode == 'Feedback'):
            if (Action == BetterStimulus):
                CorrectAction = 1
            else:
                CorrectAction = 0
        else:
            CorrectAction = []

        screen.fill(white)
        pygame.display.flip()

        if Action:
            if Action == pygame.K_1:
                Action = 1
                if (tmode == 'Feedback'):
                    Reward = LRewardGranted
                    if Reward == 0:
                        Reward -= 1
                        screen.blit(RewardSad, (((w / 2 - wRewardSad / 2, h / 2 - hRewardSad / 2))))
                        pygame.display.flip()

                    else:
                        screen.blit(RewardHappy, (((w / 2 - wRewardHappy / 2, h / 2 - hRewardHappy / 2))))
                        pygame.display.flip()


            elif Action == pygame.K_0:
                Action = 0
                if (tmode == 'Feedback'):
                    Reward = RRewardGranted
                    if Reward == 0:
                        Reward -= 1
                        screen.blit(RewardSad, (((w / 2 - wRewardSad / 2, h / 2 - hRewardSad / 2))))
                        pygame.display.flip()
                    else:
                        screen.blit(RewardHappy, (((w / 2 - wRewardHappy / 2, h / 2 - hRewardHappy / 2))))
                        pygame.display.flip()

        else:
            Action = -1
            Reward = 0
            RTime = -1
            addText('Nie udzieliłeś żadnej odpowiedzi.', red, (h / w) * 14)
            pygame.display.flip()

        if (tmode == 'Feedback'):
            elapsed_time(FeedbackPresentationTime)
            screen.fill(white)
            pygame.display.flip()
        else:
            Reward = np.array([])
            if Action == -1:
                elapsed_time(FeedbackPresentationTime)

        return Action, Reward, RTime, LStimulusNo, RStimulusNo, CorrectAction

    def slider():
        RewardSad = pygame.image.load("r_sad.png")
        sad_face_transform = pygame.transform.scale(RewardSad, (math.floor(h / 6), math.floor(h / 6)))
        s_x = 1 / 4 * w - 1 / 2 * (math.floor(h / 6))
        s_y = h - 1 / 4 * h
        screen.blit(sad_face_transform, (s_x, s_y))

        meh_face = pygame.image.load("r_meh.png")
        meh_face_transform = pygame.transform.scale(meh_face, (math.floor(h / 6), math.floor(h / 6)))
        m_x = 1 / 2 * w - 1 / 2 * (math.floor(h / 6))
        m_y = h - 1 / 4 * h
        screen.blit(meh_face_transform, (m_x, m_y))

        RewardHappy = pygame.image.load("r_happy.png")
        happy_face_transform = pygame.transform.scale(RewardHappy, (math.floor(h / 6), math.floor(h / 6)))
        h_x = 3 / 4 * w - 1 / 2 * (math.floor(h / 6))
        h_y = h - 1 / 4 * h
        screen.blit(happy_face_transform, (h_x, h_y))

        pygame.display.flip()

        percent = None
        slider_on = True
        while slider_on:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()
                    con_sad = s_x + math.floor(h / 6) > mouse[0] > s_x and s_y + math.floor(h / 6) > mouse[1] > s_y
                    con_meh = m_x + math.floor(h / 6) > mouse[0] > m_x and m_y + math.floor(h / 6) > mouse[1] > m_y
                    con_happy = h_x + math.floor(h / 6) > mouse[0] > h_x and h_y + math.floor(h / 6) > mouse[1] > h_y
                    if con_sad or con_meh or con_happy:
                        screen.fill(white)
                        pygame.display.flip()
                        pygame.display.flip()
                        xcol_sad, ycol_sad = event.pos
                        xcol_meh, ycol_meh = event.pos
                        xcol_happy, ycol_happy = event.pos
                        if sad_face_transform.get_rect(topleft=(s_x, s_y)).collidepoint((xcol_sad, ycol_sad)):
                            percent = 10
                        elif meh_face_transform.get_rect(topleft=(m_x, m_y)).collidepoint((xcol_meh, ycol_meh)):
                            percent = 50
                        elif happy_face_transform.get_rect(topleft=(h_x, h_y)).collidepoint((xcol_happy, ycol_happy)):
                            percent = 90
                        return percent

    while True:
        instruction_page = 1
        display_instructions = True
        while display_instructions == True:
            if instruction_page < 5:
                cd = getAnyKey()
                if instruction_page == 1:
                    text_all(instruction[0], black, (h / w) * 4)
                if instruction_page == 2:
                    text_all(instruction[1], black, (h / w) * 12)
                if instruction_page == 3:
                    text_all(instruction[2], black, (h / w) * 16)
                if instruction_page == 4:
                    text_all(instruction[3], black, (h / w) * 16)
                if cd == pygame.K_SPACE:
                    instruction_page += 1
            elif instruction_page == 5:
                cd = getAnyKey()
                text_all(instruction[4], black, (h / w) * 16)
                if cd == pygame.K_1:
                    instruction_page += 1
                if cd != pygame.K_1 and cd is not None:
                    instruction_page = 20
            elif instruction_page == 6:
                cd = getAnyKey()
                text_all(instruction[5], black, (h / w) * 16)
                if cd == pygame.K_0:
                    instruction_page += 1
                if cd != pygame.K_0 and cd is not None:
                    instruction_page = 21
            elif instruction_page >= 7:
                cd = getAnyKey()
                if instruction_page == 7:
                    text_all(instruction[6], black, (h / w) * 12)
                if instruction_page == 8:
                    text_all(instruction[7], black, (h / w) * 16)
                if cd == pygame.K_SPACE:
                    instruction_page += 1
            if instruction_page == 9:
                display_instructions = False
            if instruction_page == 20:
                if cd is not None:
                    if cd == 32:
                        notka = [['Niestety wybrałeś', 'spację', 'powinieneś wybrać 1.']]
                        text_all(notka[0], black, (h / w) * 14)
                        elapsed_time(1.5)
                        instruction_page = 5
                    else:
                        notka = [['Niestety wybrałeś', chr(cd), 'powinieneś wybrać 1.']]
                        text_all(notka[0], black, (h / w) * 14)
                        elapsed_time(1.5)
                        instruction_page = 5
            if instruction_page == 21:
                if cd is not None:
                    if cd == 32:
                        notka = [['Niestety wybrałeś', 'spację', 'powinieneś wybrać 0.']]
                        text_all(notka[0], black, (h / w) * 14)
                        elapsed_time(1.5)
                        instruction_page = 6
                    else:
                        notka = [['Niestety wybrałeś', chr(cd), 'powinieneś wybrać 0.']]
                        text_all(notka[0], black, (h / w) * 14)
                        elapsed_time(1.5)
                        instruction_page = 6
        screen.fill(white)
        pygame.display.flip()

        trial = True
        while trial == True:
            # x = 1 # szybka gra
            x = 6
            for i in range(x):
                showfocuspoint(1, 3)
                showtrial(6, 7, [1, 0], 'Feedback')
                if i == x - 1:
                    trial = False

        text_all(instruction[8], black, (h / w) * 8)
        while getAnyKey() != pygame.K_SPACE:
            continue

        screen.fill(white)
        pygame.display.flip()
        StimulusHistory = []
        StimulusHistoryLeft = []
        StimulusHistoryRight = []
        ActionHistory = []
        CorrectActionHistory = []
        RewardHistory = []
        RTimeHistory = []
        moreBlocks = 1
        b = 0
        ABcorrect = np.zeros(TrainingCycleLength * CycleNo)
        CDcorrect = np.zeros(TrainingCycleLength * CycleNo)
        EFcorrect = np.zeros(TrainingCycleLength * CycleNo)
        ABperformance = np.zeros(TrainingCycleLength * CycleNo)
        CDperformance = np.zeros(TrainingCycleLength * CycleNo)
        EFperformance = np.zeros(TrainingCycleLength * CycleNo)

        while moreBlocks == 1 and b <= MaximumBlocks:
            ABcorrect[b] = 0
            CDcorrect[b] = 0
            EFcorrect[b] = 0
            ABperformance[b] = 0
            CDperformance[b] = 0
            EFperformance[b] = 0

            ActionBlockHistory = np.zeros(TrainingCycleLength * CycleNo)
            CorrectActionBlockHistory = np.zeros(TrainingCycleLength * CycleNo)
            RewardBlockHistory = np.zeros(TrainingCycleLength * CycleNo)
            RTimeBlockHistory = np.zeros(TrainingCycleLength * CycleNo)
            StimulusBlockHistory = np.zeros(TrainingCycleLength * CycleNo)
            StimulusBlockHistoryLeft = np.zeros(TrainingCycleLength * CycleNo)
            StimulusBlockHistoryRight = np.zeros(TrainingCycleLength * CycleNo)

            for c in range(CycleNo):
                pairs = []
                [pairs.append(num) for num in np.arange(TrainingCycleLength)]
                pairs = np.array(list(np.random.permutation(pairs)))
                if c > 0:
                    while pairs[0] == StimulusBlockHistory[TrainingCycleLength * c]:
                        pairs = np.array(list(np.random.permutation(pairs)))
                else:
                    if b > 0:
                        while pairs[0] == StimulusHistory[len(StimulusHistory)]:
                            pairs = np.array(list(np.random.permutation(pairs)))
                StimulusBlockHistory[TrainingCycleLength * c: TrainingCycleLength * (c + 1)] = pairs

            RewardsGrantedA = np.zeros(CycleNo)
            RewardsGrantedB = np.zeros(CycleNo)
            RewardsGrantedC = np.zeros(CycleNo)
            RewardsGrantedD = np.zeros(CycleNo)
            RewardsGrantedE = np.zeros(CycleNo)
            RewardsGrantedF = np.zeros(CycleNo)
            RewardsGrantedA[0:int(CycleNo * ProbRew[0] + 1)] = 1
            RewardsGrantedB[0:int(CycleNo * ProbRew[1] + 1)] = 1
            RewardsGrantedC[0:int(CycleNo * ProbRew[2] + 1)] = 1
            RewardsGrantedD[0:int(CycleNo * ProbRew[3] + 1)] = 1
            RewardsGrantedE[0:int(CycleNo * ProbRew[4] + 1)] = 1
            RewardsGrantedF[0:int(CycleNo * ProbRew[5] + 1)] = 1
            RewardsGranted = np.zeros((2, TrainingCycleLength * CycleNo))

            idx1 = StimulusBlockHistory == 0
            idx2 = StimulusBlockHistory == 1
            idx3 = StimulusBlockHistory == 2

            RewardsGranted[0, idx1] = RewardsGrantedA[np.random.permutation(CycleNo)]
            RewardsGranted[1, idx1] = RewardsGrantedB[np.random.permutation(CycleNo)]
            RewardsGranted[0, idx2] = RewardsGrantedC[np.random.permutation(CycleNo)]
            RewardsGranted[1, idx2] = RewardsGrantedD[np.random.permutation(CycleNo)]
            RewardsGranted[0, idx3] = RewardsGrantedE[np.random.permutation(CycleNo)]
            RewardsGranted[1, idx3] = RewardsGrantedF[np.random.permutation(CycleNo)]

            for i in range(TrainingCycleLength * CycleNo):
                showfocuspoint(1, 3)
                ActionBlockHistory[i], RewardBlockHistory[i], RTimeBlockHistory[i], \
                StimulusBlockHistoryLeft[i], StimulusBlockHistoryRight[i], CorrectActionBlockHistory[i] \
                    = showtrial(2 * int(StimulusBlockHistory[i]), 2 * int(StimulusBlockHistory[i]) + 1,
                                RewardsGranted[:, i], 'Feedback')

            ABcorrect[b] = sum((CorrectActionBlockHistory == 1) * (StimulusBlockHistory == 1))
            CDcorrect[b] = sum((CorrectActionBlockHistory == 1) * (StimulusBlockHistory == 2))
            EFcorrect[b] = sum((CorrectActionBlockHistory == 1) * (StimulusBlockHistory == 3))

            StimulusHistory = np.concatenate((StimulusHistory, StimulusBlockHistory), axis=0)
            StimulusHistoryLeft = np.concatenate((StimulusHistoryLeft, StimulusBlockHistoryLeft), axis=0)
            StimulusHistoryRight = np.concatenate((StimulusHistoryRight, StimulusBlockHistoryRight), axis=0)
            ActionHistory = np.concatenate((ActionHistory, ActionBlockHistory), axis=0)
            CorrectActionHistory = np.concatenate((CorrectActionHistory, CorrectActionBlockHistory), axis=0)
            RewardHistory = np.concatenate((RewardHistory, RewardBlockHistory), axis=0)
            RTimeHistory = np.concatenate((RTimeHistory, RTimeBlockHistory), axis=0)

            ABperformance[b] = ABcorrect[b] / CycleNo
            CDperformance[b] = CDcorrect[b] / CycleNo
            EFperformance[b] = EFcorrect[b] / CycleNo
            print(ABperformance)

            if b >= MinimumBlocks and ABperformance[b] >= 65 / 100 and CDperformance[b] >= 60 / 100 and EFperformance[
                b] >= 50 / 100:
                moreBlocks = 0

            b += 1

            if moreBlocks == 1 and b <= MaximumBlocks and b >= MinimumBlocks:
                text_all(instruction[9], black, 8)
                if getAnyKey() == pygame.K_SPACE:
                    continue
                while getAnyKey() != pygame.K_SPACE:
                    continue
                screen.fill(white)
                pygame.display.flip()
            break

        text_all(instruction[10], black, (h / w) * 16)
        elapsed_time(4)
        screen.fill(white)

        # zapisywanie wyników 'learning'
        learning_dict = {'StimulusPair': StimulusHistory, 'StimulusLeft': StimulusHistoryLeft,
                         'StimulusRight': StimulusHistoryRight, 'Action': ActionHistory,
                         'Was the Action Correct?': CorrectActionHistory, 'Reward': RewardHistory,
                         'Response time': RTimeHistory}
        learning_df = (pd.DataFrame(learning_dict, columns=['StimulusPair', 'StimulusLeft', 'StimulusRight', 'Action',
                                                            'Was the Action Correct?', 'Reward', 'Response time'])).T

        writer_learning = pd.ExcelWriter(learning_path, engine='xlwt')
        learning_df.to_excel(writer_learning, header=False)
        writer_learning.save()

        writer_person_learning = pd.ExcelWriter(person_learning_path, engine='xlwt')
        learning_df.to_excel(writer_person_learning, header=False)
        writer_person_learning.save()

        text_all(instruction[11], black, (h / w) * 12)
        while getAnyKey() != pygame.K_SPACE:
            continue
        screen.fill(white)
        text_all(instruction[12], black, (h / w) * 16)
        while getAnyKey() != pygame.K_SPACE:
            continue
        screen.fill(white)
        text_all(instruction[13], black, (h / w) * 12)
        while getAnyKey() != pygame.K_SPACE:
            continue
        screen.fill(white)
        text_all(instruction[14], black, (h / w) * 16)
        elapsed_time(1)
        screen.fill(white)

        M = 6
        TotalPairs = int(M * (M - 1) / 2)
        stimulipairs = np.zeros((TotalPairs, 3))
        k = 0
        for i in range(M - 1):
            for j in range(i + 1, M):
                stimulipairs[k, 0:2] = np.array([i, j])
                k += 1

        occurence = np.zeros(len(stimulipairs))
        for i in range(len(stimulipairs)):
            if stimulipairs[i, 0] == 1 and stimulipairs[i, 1] == 2 or stimulipairs[i, 0] == 3 and stimulipairs[
                i, 1] == 4 or stimulipairs[i, 0] == 5 and stimulipairs[i, 1] == 6:
                occurence[i] = 1
            else:
                occurence[i] = 6

        for i in range(len(stimulipairs)):
            stimulipairs[i, 2] = occurence[i]

        stimulipairs = stimulipairs[stimulipairs[:, 0].argsort()]
        oldstimulipairs = stimulipairs[stimulipairs[:, 2] == 1, :]
        newstimulipairs = stimulipairs[stimulipairs[:, 2] == 6, :]
        oldstimulipairs = np.delete(oldstimulipairs, 2, 1)
        newstimulipairs = np.delete(newstimulipairs, 2, 1)
        stimulisession = np.concatenate((oldstimulipairs, newstimulipairs[np.random.permutation(len(newstimulipairs))]),
                                        axis=0)

        for i in range(1, 6):
            addstimulipairs = newstimulipairs[np.random.permutation(len(newstimulipairs)), :]
            while addstimulipairs[0, 0] == stimulisession[len(stimulisession) - 1, 0] and addstimulipairs[0, 1] == \
                    stimulisession[len(stimulisession) - 1, 1]:
                addstimulipairs = newstimulipairs[np.random.permutation(len(newstimulipairs)), :]
            stimulisession = np.concatenate((stimulisession, addstimulipairs), axis=0)

        StimulusHistoryLeft = np.transpose(stimulisession[:, 0])
        StimulusHistoryRight = np.transpose(stimulisession[:, 1])
        ActionHistory = np.zeros(len(stimulisession))
        RTimeHistory = np.zeros(len(stimulisession))

        for i in range(len(stimulisession)):
            # for i in range(1):  # szybka gra
            showfocuspoint(1, 3)
            ActionHistory[i], _, RTimeHistory[i], _, _, _ = showtrial(int(stimulisession[i, 0]),
                                                                      int(stimulisession[i, 1]), [], 'No Feedback')
        text_all(instruction[15], black, (h / w) * 8)
        while getAnyKey() != pygame.K_SPACE:
            continue

        UserProbabilities = np.zeros(6)
        for judge_image in range(6):
            screen.fill(white)
            pygame.display.flip()
            the_image = pygame.image.load(Stimulus[judge_image])
            the_image_scaled = pygame.transform.scale(the_image, (math.floor(h / 2), math.floor(h / 2)))
            wji = pygame.Surface.get_width(the_image_scaled)
            hji = pygame.Surface.get_height(the_image_scaled)
            showfocuspoint(1, 3)
            screen.fill(white)
            pygame.display.flip()
            screen.blit(the_image_scaled, (((w / 2 - wji / 2, h / 3 - hji / 2))))
            pygame.display.flip()
            percent = slider()
            UserProbabilities[judge_image] = percent

        # UserProbabilities - pobrane wartości są różne od zera
        UserProbabilities = np.concatenate((UserProbabilities, np.zeros(len(ActionHistory) - len(UserProbabilities))),
                                           axis=0)

        # zapisywanie wyników 'testing'
        testing_dict = {'StimulusLeft': StimulusHistoryLeft, 'StimulusRight': StimulusHistoryRight,
                        'Action': ActionHistory, 'Response time': RTimeHistory, 'UserProbabilities': UserProbabilities}
        testing_df = (pd.DataFrame(testing_dict, columns=['StimulusLeft', 'StimulusRight', 'Action', 'Response time',
                                                          'UserProbabilities'])).T

        writer_testing = pd.ExcelWriter(testing_path, engine='xlwt')
        testing_df.to_excel(writer_testing, header=False)
        writer_testing.save()

        writer_person_testing = pd.ExcelWriter(person_testing_path, engine='xlwt')
        testing_df.to_excel(writer_person_testing, header=False)
        writer_person_testing.save()

        screen.fill(white)
        pygame.display.flip()
        text_all(instruction[16], black, (h / w) * 16)
        elapsed_time(3)

        screen.fill(white)
        pygame.display.flip()
        text_all(instruction[17], black, (h / w) * 20)
        while getAnyKey() != pygame.K_SPACE:
            continue

        screen.fill(white)
        pygame.display.flip()
        text_all(instruction[18], black, (h / w) * 10)
        while getAnyKey() != pygame.K_SPACE:
            continue
        break


################################################-GUI-############################################################


def entry_gui():
    # parametry okna
    root = Tk()
    root.title("Parametry")
    root.geometry("250x470")
    ramka = Frame(root)
    ramka.grid()
    # etykieta instrukcji
    tutor = Label(ramka, text="Wypełnij wszystkie poniższe pola.")
    tutor.grid(row=0, column=0, columnspan=2, sticky=S)
    # pusta linijka
    empty1 = Label(ramka, text=' ')
    empty1.grid(row=1, column=0, columnspan=2, sticky=S)
    # utworz w ramce etykiete IMIĘ
    name_value = StringVar()
    name = Label(ramka, text="Imię:")
    name.grid(row=2, column=0, sticky=S)
    # widget do przyjęcia imienia
    name_w = Entry(ramka, textvariable=name_value)
    name_w.grid(row=3, column=0, sticky=S)
    # etykieta NAZWISKO
    surname_value = StringVar()
    surname = Label(ramka, text="Nazwisko:")
    surname.grid(row=2, column=1, sticky=S)
    # widget do przyjęcia nazwiska
    surname_w = Entry(ramka, textvariable=surname_value)
    surname_w.grid(row=3, column=1, sticky=S)
    # pusta linijka
    empty2 = Label(ramka, text=' ')
    empty2.grid(row=4, column=0, columnspan=2, sticky=S)
    # etykieta CycleNo
    c_no_value = IntVar(ramka, value=10)
    c_no = Label(ramka, text="Liczba cykli:")
    c_no.grid(row=5, column=0, columnspan=2, sticky=S)
    # widget
    c_no_w = Entry(ramka, textvariable=c_no_value)
    c_no_w.grid(row=6, column=0, columnspan=2, sticky=S)
    # etykieta MinimumBlocks
    min_bl_value = IntVar(ramka, value=2)
    min_bl = Label(ramka, text="Min. liczba bloków:")
    min_bl.grid(row=7, column=0, columnspan=2, sticky=S)
    # widget
    min_bl_w = Entry(ramka, textvariable=min_bl_value)
    min_bl_w.grid(row=8, column=0, columnspan=2, sticky=S)
    # etykieta MaximumBlocks
    max_bl_value = IntVar(ramka, value=4)
    max_bl = Label(ramka, text="Maks. liczba bloków:")
    max_bl.grid(row=9, column=0, columnspan=2, sticky=S)
    # widget
    max_bl_w = Entry(ramka, textvariable=max_bl_value)
    max_bl_w.grid(row=10, column=0, columnspan=2, sticky=S)
    # pusta linijka
    empty3 = Label(ramka, text=' ')
    empty3.grid(row=11, column=0, columnspan=2, sticky=S)
    # etykieta PRAWDOPODOBIEŃSTWA
    prob1_value = IntVar(ramka, value=90)
    prob2_value = IntVar(ramka, value=15)
    prob3_value = IntVar(ramka, value=80)
    prob4_value = IntVar(ramka, value=30)
    prob5_value = IntVar(ramka, value=80)
    prob6_value = IntVar(ramka, value=30)
    prob = Label(ramka, text="Prawdopodobieństwa [%]:")
    prob.grid(row=12, column=0, columnspan=2, sticky=S)
    # widgety
    prob_w1 = Entry(ramka, textvariable=prob1_value)
    prob_w1.grid(row=13, column=0, columnspan=2, sticky=S)
    prob_w2 = Entry(ramka, textvariable=prob2_value)
    prob_w2.grid(row=14, column=0, columnspan=2, sticky=S)
    prob_w3 = Entry(ramka, textvariable=prob3_value)
    prob_w3.grid(row=15, column=0, columnspan=2, sticky=S)
    prob_w4 = Entry(ramka, textvariable=prob4_value)
    prob_w4.grid(row=16, column=0, columnspan=2, sticky=S)
    prob_w5 = Entry(ramka, textvariable=prob5_value)
    prob_w5.grid(row=17, column=0, columnspan=2, sticky=S)
    prob_w6 = Entry(ramka, textvariable=prob6_value)
    prob_w6.grid(row=18, column=0, columnspan=2, sticky=S)
    # pusta linijka
    empty4 = Label(ramka, text=' ')
    empty4.grid(row=19, column=0, columnspan=2, sticky=S)

    def saving():
        ProbRew = np.zeros(6)
        ProbRew[0] = prob1_value.get()
        ProbRew[1] = prob2_value.get()
        ProbRew[2] = prob3_value.get()
        ProbRew[3] = prob4_value.get()
        ProbRew[4] = prob5_value.get()
        ProbRew[5] = prob6_value.get()
        return name_value.get(), surname_value.get(), c_no_value.get(), min_bl_value.get(), max_bl_value.get(), ProbRew

    def save_and_quit():
        saving()
        root.destroy()

    def close_window():
        root.destroy()
        sys.exit()

    # przycisk akceptacji
    button_akcept = Button(ramka, text="Akceptuj", command=save_and_quit)
    button_akcept.grid(row=20, column=0, columnspan=2, sticky=S)

    # przycisk zamykania
    button_close = Button(ramka, text="Anuluj", command=close_window)
    button_close.grid(row=21, column=0, columnspan=2, sticky=S)

    def do_nothing():
        pass

    # krzyżyk zamykania
    root.protocol("WM_DELETE_WINDOW", do_nothing)

    # uruchom pętlę zdarzeń
    root.mainloop()

    imie, nazwisko, CycleNo, MinimumBlocks, MaximumBlocks, ProbRew = saving()
    ProbRew = ProbRew / 100
    filename = imie + nazwisko

    return filename, CycleNo, MinimumBlocks, MaximumBlocks, ProbRew


#################################################################################################################

filename, CycleNo, MinimumBlocks, MaximumBlocks, ProbRew = entry_gui()
runtest(filename, CycleNo, MinimumBlocks, MaximumBlocks, ProbRew)