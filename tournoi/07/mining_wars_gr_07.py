import os
from termcolor import colored
import random
import remote_play as rp
import AI
import sys
import datetime

def main(player1, player2, config="./config.mw", log=False, log_path='.\log\default_log.txt', turn_wo_dmg_max=20):
    """The main function of the game. Calls all other functions to run the game.

    Parameters
    ----------
    player1: information about first player (name, type, (IP)) (tuple)
    player2: information about second player (name, type, (IP)) (tuple)
    config: path to the config file (str, defaut ./config.mw)
    log: do we print in a log file ? (bool, optional)
    log_path: the path to the log file (str, optional)
    turn_wo_dmg_max: the maximum turn without damage before the games end (int, optional)
    
    Notes
    -----
    Player info should look like this ('name', 'type', 'IP' if type is remote). 
    Type must be 'human', 'AI' or 'remote'
    Cannot use two 'remote' players
    
    Version
    -------
    Specifications: Jules Dejaeghere (v.1 27/02/2018)
                    Jules Dejaeghere (v.2 23/03/2018)
                    Martin Balfroid (v.3 05/05/2018)
                    Martin Balfroid (v.4 06/05/2018)
    Implementation: Jules Dejaeghere (v.1 07/03/2018)
                    Martin Balfroid  (v.2 08/03/2018)
                    Jules Dejaeghere (v.3 15/03/2018)
                    Jules Dejaeghere (v.4 23/03/2018)
                    Jules Dejaeghere (v.5 15/04/2018)
                    Martin Balfroid (v.6 05/05/2018)
    """

    # ------------Creation of info_ship structure------------#
    # SCOUT
    scout_fig = list()
    for y in range(-1, 1 + 1):
        scout_fig += [(y, x) for x in range(-1, 1 + 1) if (y, x) != (0, 0)]

    # EXCAVATOR_L
    excavator_l_fig = [(0, x) for x in range(-2, 2 + 1) if x != 0]
    excavator_l_fig += [(y, 0) for y in range(-2, 2 + 1) if y != 0]

    # WARSHIP
    warship_fig = []
    for y in range(-2, 2 + 1):
        warship_fig += [(y, x) for x in range(-2, 2 + 1) if (
            not (y, x) in [(0, 0), (-2, -2), (-2, 2), (2, 2), (2, -2)])]

    info_ships = {
        'scout': {'size': 9, 'max_load': 0, 'life': 3, 'attack': 1,
                  'range': 3, 'cost': 3, 'lockable': False, 'fig': scout_fig},

        'warship': {'size': 21, 'max_load': 0, 'life': 18, 'attack': 3,
                    'range': 5, 'cost': 9, 'lockable': False, 'fig': warship_fig},

        'excavator-S': {'size': 1, 'max_load': 1, 'life': 2, 'attack': 0,
                        'range': 0, 'cost': 1, 'lockable': True, 'fig': []},

        'excavator-M': {'size': 5, 'max_load': 4, 'life': 3, 'attack': 0,
                        'range': 0, 'cost': 2, 'lockable': True, 'fig': [(-1, 0), (0, -1), (0, 1), (1, 0)]},

        'excavator-L': {'size': 9, 'max_load': 8, 'life': 6, 'attack': 0,
                        'range': 0, 'cost': 4, 'lockable': True, 'fig': excavator_l_fig}}
    # -------------------------------------------------------------- #

    # ------------Init game and create data structure------------ #
    error = False
    asteroids, map_width, map_height = list(), 0, 0
    
    error = player1[1] == 'remote' and player2[1] == 'remote'
    
    remote_player_id, remote_IP = None, None
    
    for index, player in enumerate((player1, player2)):
        if player[1] == 'remote':
            remote_player_id = index+1
            remote_IP = player[2]
    
    if remote_IP != None:
        connection = rp.connect_to_player(remote_player_id, remote_IP, True) 
    else:
        connection = None
    
    try:
        players, asteroids, map_width, map_height = start(player1, player2, config)
    except TypeError:
        error = True
        players = list()

    ships = dict()
    turn, turn_wo_dmg = 0, 0
    over = False
    AI_data = dict()

    # List of names taken from 
    # http://www.quietaffiliate.com/free-first-name-and-last-name-databases-csv-and-sql/
    # List(str)
    AI_data['name'] = ['Aaron', 'Abbey', 'Abbie', 'Abby', 'Abdul', 'Abe', 'Abel', 'Abigail', 'Abraham', 'Abram', 'Ada', 'Adah', 'Adalberto', 'Adaline', 'Adam', 'Adan', 'Addie', 'Adela', 'Adelaida', 'Adelaide', 'Adele', 'Adelia', 'Adelina', 'Adeline', 'Adell', 'Adella', 'Adelle', 'Adena', 'Adina', 'Adolfo', 'Adolph', 'Adria', 'Adrian', 'Adriana', 'Adriane', 'Adrianna', 'Adrianne', 'Adrien', 'Adriene', 'Adrienne', 'Afton', 'Agatha', 'Agnes', 'Agnus', 'Agripina', 'Agueda', 'Agustin', 'Agustina', 'Ahmad', 'Ahmed', 'Ai', 'Aida', 'Aide', 'Aiko', 'Aileen', 'Ailene', 'Aimee', 'Aisha', 'Aja', 'Akiko', 'Akilah', 'Al', 'Alaina', 'Alaine', 'Alan', 'Alana', 'Alane', 'Alanna', 'Alayna', 'Alba', 'Albert', 'Alberta', 'Albertha', 'Albertina', 'Albertine', 'Alberto', 'Albina', 'Alda', 'Alden', 'Aldo', 'Alease', 'Alec', 'Alecia', 'Aleen', 'Aleida', 'Aleisha', 'Alejandra', 'Alejandrina', 'Alejandro', 'Alena', 'Alene', 'Alesha', 'Aleshia', 'Alesia', 'Alessandra', 'Aleta', 'Aletha', 'Alethea', 'Alethia', 'Alex', 'Alexa', 'Alexander', 'Alexandrie_Alexandra', 'Alexandria', 'Alexia', 'Alexis', 'Alfonso', 'Alfonzo', 'Alfred', 'Alfreda', 'Alfredia', 'Alfredo', 'Ali', 'Alia', 'Alica', 'Alice', 'Alicia', 'Alida', 'Alina', 'Aline', 'Alisa', 'Alise', 'Alisha', 'Alishia', 'Alisia', 'Alison', 'Alissa', 'Alita', 'Alix', 'Aliza', 'Alla', 'Allan', 'Alleen', 'Allegra', 'Allen', 'Allena', 'Allene', 'Allie', 'Alline', 'Allison', 'Allyn', 'Allyson', 'Alma', 'Almeda', 'Almeta', 'Alona', 'Alonso', 'Alonzo', 'Alpha', 'Alphonse', 'Alphonso', 'Alta', 'Altagracia', 'Altha', 'Althea', 'Alton', 'Alva', 'Alvaro', 'Alvera', 'Alverta', 'Alvin', 'Alvina', 'Alyce', 'Alycia', 'Alysa', 'Alyse', 'Alysha', 'Alysia', 'Alyson', 'Alyssa', 'Amada', 'Amado', 'Amal', 'Amalia', 'Amanda', 'Amber', 'Amberly', 'Ambrose', 'Amee', 'Amelia', 'America_Greatagain', 'Ami_Calment', 'Amie', 'Amiee', 'Amina', 'Amira', 'Ammie', 'Amos', 'Amparo', 'Amy', 'An', 'Ana', 'Anabel', 'Analisa', 'Anamaria', 'Anastacia', 'Anastasia', 'Andera', 'Anderson', 'Andra', 'Andre', 'Andrea', 'Andreas', 'Andree', 'Andres', 'Andrew', 'Andria', 'Andy', 'Anette', 'Angel', 'Angela', 'Angele', 'Angelena', 'Angeles', 'Angelia', 'Angelic', 'Angelica', 'Angelika', 'Angelina', 'Angeline', 'Angelique', 'Angelita', 'Angella', 'Angelo', 'Angelyn', 'Angie', 'Angila', 'Angla', 'Angle', 'Anglea', 'Anh', 'Anibal', 'Anika', 'Anisa', 'Anisha', 'Anissa', 'Anita', 'Anitra', 'Anja', 'Anjanette', 'Anjelica', 'Ann', 'Anna', 'Annabel', 'Annabell', 'Annabelle', 'Annalee', 'Annalisa', 'Annamae', 'Annamaria', 'Annamarie', 'Anne', 'Anneliese', 'Annelle', 'Annemarie', 'Annett', 'Annetta', 'Annette', 'Annice', 'Annie_Versaire', 'Annika', 'Annis', 'Annita', 'Annmarie', 'Anthony', 'Antione', 'Antionette', 'Antoine', 'Antoinette', 'Anton', 'Antone', 'Antonetta', 'Antonette', 'Antonia', 'Antonietta', 'Antonina', 'Antonio', 'Antony', 'Antwan', 'Anya', 'Apolonia', 'April', 'Apryl', 'Ara', 'Araceli', 'Aracelis', 'Aracely', 'Arcelia', 'Archie', 'Ardath', 'Ardelia', 'Ardell', 'Ardella', 'Ardelle', 'Arden', 'Ardis', 'Ardith', 'Aretha', 'Argelia', 'Argentina', 'Ariana', 'Ariane', 'Arianna', 'Arianne', 'Arica', 'Arie', 'Ariel', 'Arielle', 'Arla', 'Arlean', 'Arleen', 'Arlen', 'Arlena', 'Arlene', 'Arletha', 'Arletta', 'Arlette', 'Arlie', 'Arlinda', 'Arline', 'Arlyne', 'Armand', 'Armanda', 'Armandina', 'Armando', 'Armida', 'Arminda', 'Arnetta', 'Arnette', 'Arnita', 'Arnold', 'Arnoldo', 'Arnulfo', 'Aron', 'Arron', 'Art', 'Arthur', 'Artie', 'Arturo', 'Arvilla', 'Asa', 'Asha', 'Ashanti', 'Ashely', 'Ashlea', 'Ashlee', 'Ashleigh', 'Ashley', 'Ashli', 'Ashlie', 'Ashly', 'Ashlyn', 'Ashton', 'Asia', 'Asley', 'Assunta', 'Astrid', 'Asuncion', 'Athena', 'Aubrey', 'Audie', 'Audra', 'Audrea', 'Audrey', 'Audria', 'Audrie', 'Audry', 'August', 'Augusta', 'Augustina', 'Augustine', 'Augustus', 'Aundrea', 'Aura', 'Aurea', 'Aurelia', 'Aurelio', 'Aurora', 'Aurore', 'Austin', 'Autumn', 'Ava', 'Avelina', 'Avery', 'Avis', 'Avril', 'Awilda', 'Ayako', 'Ayana', 'Ayanna', 'Ayesha', 'Azalee', 'Azucena', 'Azzie', 'Babara', 'Babette', 'Bailey', 'Bambi', 'Bao', 'Barabara', 'Barb', 'Barbar', 'Barbara', 'Barbera', 'Barbie', 'Barbra', 'Bari', 'Barney', 'Barrett', 'Barrie', 'Barry_Allen_the_fastest_ship_alive', 'Bart', 'Barton', 'Basil_Simple', 'Basilia', 'Bea', 'Beata', 'Beatrice', 'Beatris', 'Beatriz', 'Beau', 'Beaulah', 'Bebe', 'Becki', 'Beckie', 'Becky', 'Bee', 'Belen', 'Belia', 'Belinda', 'Belkis', 'Bell', 'Bella', 'Belle', 'Belva', 'Ben', 'Benedict', 'Benita', 'Benito', 'Benjamin', 'Bennett', 'Bennie', 'Benny', 'Benton', 'Berenice', 'Berna', 'Bernadette', 'Bernadine', 'Bernard', 'Bernarda', 'Bernardina', 'Bernardine', 'Bernardo', 'Berneice', 'Bernetta', 'Bernice', 'Bernie', 'Berniece', 'Bernita', 'Berry', 'Bert', 'Berta', 'Bertha', 'Bertie', 'Bertram', 'Beryl', 'Bess', 'Bessie', 'Beth', 'Bethanie', 'Bethann', 'Bethany', 'Bethel', 'Betsey', 'Betsy', 'Bette', 'Bettie', 'Bettina', 'Betty', 'Bettyann', 'Bettye', 'Beula', 'Beulah', 'Bev', 'Beverlee', 'Beverley', 'Beverly', 'Bianca', 'Bibi', 'Bill', 'Billi', 'Billie', 'Billy', 'Billye', 'Birdie', 'Birgit', 'Blaine', 'Blair', 'Blake', 'Blanca', 'Blanch', 'Blanche', 'Blondell', 'Blossom', 'Blythe', 'Bo', 'Bob', 'Bobbi', 'Bobbie', 'Bobby', 'Bobbye', 'Bobette', 'Bok', 'Bong', 'Bonita', 'Bonnie', 'Bonny', 'Booker', 'Boris', 'Boyce', 'Boyd', 'Brad', 'Bradford', 'Bradley', 'Bradly', 'Brady', 'Brain', 'Branda', 'Brande', 'Brandee', 'Branden', 'Brandi', 'Brandie', 'Brandon', 'Brandy', 'Brant', 'Breana', 'Breann', 'Breanna', 'Breanne', 'Bree', 'Brenda', 'Brendan', 'Brendon', 'Brenna', 'Brent', 'Brenton', 'Bret', 'Brett', 'Brian', 'Briana', 'Brianna', 'Brianne', 'Brice_de_Nice', 'Bridget', 'Bridgett', 'Bridgette', 'Brigette', 'Brigid', 'Brigida', 'Brigitte', 'Brinda', 'Britany', 'Britney', 'Britni', 'Britt', 'Britta', 'Brittaney', 'Brittani', 'Brittanie', 'Brittany', 'Britteny', 'Brittney', 'Brittni', 'Brittny', 'Brock', 'Broderick', 'Bronwyn', 'Brook', 'Brooke', 'Brooks', 'Bruce', 'Bruna', 'Brunilda', 'Bruno', 'Bryan', 'Bryanna', 'Bryant', 'Bryce', 'Brynn', 'Bryon', 'Buck', 'Bud', 'Buddy', 'Buena', 'Buffy', 'Buford', 'Bula', 'Bulah', 'Bunny', 'Burl', 'Burma', 'Burt', 'Burton', 'Buster', 'Byron', 'Caitlin', 'Caitlyn', 'Calandra', 'Caleb', 'Calista', 'Callie', 'Calvin', 'Camelia', 'Camellia', 'Cameron', 'Cami', 'Camie', 'Camila', 'Camilla', 'Camille', 'Cammie', 'Cammy', 'Candace', 'Candance', 'Candelaria', 'Candi', 'Candice', 'Candida', 'Candie', 'Candis', 'Candra', 'Candy', 'Candyce', 'Caprice', 'Cara', 'Caren', 'Carey', 'Cari', 'Caridad', 'Carie', 'Carin', 'Carina', 'Carisa', 'Carissa', 'Carita', 'Carl', 'Carla', 'Carlee', 'Carleen', 'Carlena', 'Carlene', 'Carletta', 'Carley', 'Carli', 'Carlie', 'Carline', 'Carlita', 'Carlo', 'Carlos', 'Carlota', 'Carlotta', 'Carlton', 'Carly', 'Carlyn', 'Carma', 'Carman', 'Carmel', 'Carmela', 'Carmelia', 'Carmelina', 'Carmelita', 'Carmella', 'Carmelo', 'Carmen', 'Carmina', 'Carmine', 'Carmon', 'Carol', 'Carola', 'Carolann', 'Carole', 'Carolee', 'Carolin', 'Carolina', 'Caroline', 'Caroll', 'Carolyn', 'Carolyne', 'Carolynn', 'Caron', 'Caroyln', 'Carri', 'Carrie', 'Carrol', 'Carroll', 'Carry', 'Carson', 'Carter', 'Cary', 'Caryl', 'Carylon', 'Caryn', 'Casandra', 'Casey', 'Casie', 'Casimira', 'Cassandra', 'Cassaundra', 'Cassey', 'Cassi', 'Cassidy', 'Cassie', 'Cassondra', 'Cassy', 'Catalina', 'Catarina', 'Caterina', 'Catharine', 'Catherin', 'Catherina', 'Catherine', 'Cathern', 'Catheryn', 'Cathey', 'Cathi', 'Cathie', 'Cathleen', 'Cathrine', 'Cathryn', 'Cathy', 'Catina', 'Catrice', 'Catrina', 'Cayla', 'Cecelia', 'Cecil', 'Cecila', 'Cecile', 'Cecilia', 'Cecille', 'Cecily', 'Cedric', 'Cedrick', 'Celena', 'Celesta', 'Celeste', 'Celestina', 'Celestine', 'Celia', 'Celina', 'Celinda', 'Celine', 'Celsa', 'Ceola', 'Cesar', 'Chad', 'Chadwick', 'Chae', 'Chan', 'Chana', 'Chance', 'Chanda', 'Chandra', 'Chanel', 'Chanell', 'Chanelle', 'Chang', 'Chantal', 'Chantay', 'Chante', 'Chantel', 'Chantell', 'Chantelle', 'Chara', 'Charis', 'Charise', 'Charissa', 'Charisse', 'Charita', 'Charity', 'Charla', 'Charleen', 'Charlena', 'Charlene', 'Charles', 'Charlesetta', 'Charlette', 'Charley', 'Charlie', 'Charline', 'Charlott', 'Charlotte', 'Charlsie', 'Charlyn', 'Charmain', 'Charmaine', 'Charolette', 'Chas', 'Chase', 'Chasidy', 'Chasity', 'Chassidy', 'Chastity', 'Chau', 'Chauncey', 'Chaya', 'Chelsea', 'Chelsey', 'Chelsie', 'Cher', 'Chere', 'Cheree', 'Cherelle', 'Cheri', 'Cherie', 'Cherilyn', 'Cherise', 'Cherish', 'Cherly', 'Cherlyn', 'Cherri', 'Cherrie', 'Cherry', 'Cherryl', 'Chery', 'Cheryl', 'Cheryle', 'Cheryll', 'Chester', 'Chet', 'Cheyenne', 'Chi', 'Chia', 'Chieko', 'Chin', 'China', 'Ching', 'Chiquita', 'Chloe', 'Chong', 'Chris', 'Chrissy', 'Christa', 'Christal', 'Christeen', 'Christel', 'Christen', 'Christena', 'Christene', 'Christi', 'Christia', 'Christian', 'Christiana', 'Christiane', 'Christie', 'Christin', 'Christina', 'Christine', 'Christinia', 'Christoper', 'Christopher', 'Christy', 'Chrystal', 'Chu', 'Chuck', 'Chun', 'Chung', 'Ciara', 'Cicely', 'Ciera', 'Cierra', 'Cinda', 'Cinderella', 'Cindi', 'Cindie', 'Cindy', 'Cinthia', 'Cira', 'Clair', 'Claire', 'Clara', 'Clare', 'Clarence', 'Claretha', 'Claretta', 'Claribel', 'Clarice', 'Clarinda', 'Clarine', 'Claris', 'Clarisa', 'Clarissa', 'Clarita', 'Clark', 'Classie', 'Claud', 'Claude', 'Claudette', 'Claudia', 'Claudie', 'Claudine', 'Claudio', 'Clay', 'Clayton', 'Clelia', 'Clemencia', 'Clement', 'Clemente', 'Clementina', 'Clementine', 'Clemmie', 'Cleo', 'Cleopatra', 'Cleora', 'Cleotilde', 'Cleta', 'Cletus', 'Cleveland', 'Cliff', 'Clifford', 'Clifton', 'Clint', 'Clinton', 'Clora', 'Clorinda', 'Clotilde', 'Clyde', 'Codi', 'Cody', 'Colby', 'Cole', 'Coleen', 'Coleman', 'Colene', 'Coletta', 'Colette', 'Colin', 'Colleen', 'Collen', 'Collene', 'Collette', 'Collin', 'Colton', 'Columbus', 'Concepcion', 'Conception', 'Concetta', 'Concha', 'Conchita', 'Connie', 'Conrad', 'Constance', 'Consuela', 'Consuelo', 'Contessa', 'Cora', 'Coral', 'Coralee', 'Coralie', 'Corazon', 'Cordelia', 'Cordell', 'Cordia', 'Cordie', 'Coreen', 'Corene', 'Coretta', 'Corey', 'Cori', 'Corie', 'Corina', 'Corine', 'Corinna', 'Corinne', 'Corliss', 'Cornelia', 'Cornelius', 'Cornell', 'Corrie', 'Corrin', 'Corrina', 'Corrine', 'Corrinne', 'Cortez', 'Cortney', 'Cory', 'Courtney', 'Coy', 'Craig', 'Creola', 'Cris', 'Criselda', 'Crissy', 'Crista', 'Cristal', 'Cristen', 'Cristi', 'Cristie', 'Cristin', 'Cristina', 'Cristine', 'Cristobal', 'Cristopher', 'Cristy', 'Cruz', 'Crysta', 'Crystal', 'Crystle', 'Cuc', 'Curt', 'Curtis', 'Cyndi', 'Cyndy', 'Cynthia', 'Cyril', 'Cyrstal', 'Cyrus', 'Cythia', 'Dacia', 'Dagmar', 'Dagny', 'Dahlia', 'Daina', 'Daine', 'Daisey', 'Daisy', 'Dakota', 'Dale', 'Dalene', 'Dalia', 'Dalila', 'Dallas', 'Dalton', 'Damaris', 'Damian', 'Damien', 'Damion', 'Damon', 'Dan', 'Dana', 'Danae', 'Dane', 'Danelle', 'Danette', 'Dani', 'Dania', 'Danial', 'Danica', 'Daniel', 'Daniela', 'Daniele', 'Daniell', 'Daniella', 'Danielle', 'Danika', 'Danille', 'Danilo', 'Danita', 'Dann', 'Danna', 'Dannette', 'Dannie', 'Dannielle', 'Danny', 'Dante', 'Danuta', 'Danyel', 'Danyell', 'Danyelle', 'Daphine', 'Daphne', 'Dara', 'Darby', 'Darcel', 'Darcey', 'Darci', 'Darcie', 'Darcy', 'Darell', 'Daren', 'Daria', 'Darin', 'Dario', 'Darius', 'Darla', 'Darleen', 'Darlena', 'Darlene', 'Darline', 'Darnell', 'Daron', 'Darrel', 'Darrell', 'Darren', 'Darrick', 'Darrin', 'Darron', 'Darryl', 'Darwin', 'Daryl', 'Dave', 'David', 'Davida', 'Davina', 'Davis', 'Dawn', 'Dawna', 'Dawne', 'Dayle', 'Dayna', 'Daysi', 'Deadra', 'Dean', 'Deana', 'Deandra', 'Deandre', 'Deandrea', 'Deane', 'Deangelo', 'Deann', 'Deanna', 'Deanne', 'Deb', 'Debbi', 'Debbie', 'Debbra', 'Debby', 'Debera', 'Debi', 'Debora', 'Deborah', 'Debra', 'Debrah', 'Debroah', 'Dede', 'Dedra', 'Dee', 'Deeann', 'Deeanna', 'Deedee', 'Deedra', 'Deena', 'Deetta', 'Deidra', 'Deidre', 'Deirdre', 'Deja', 'Del', 'Delaine', 'Delana', 'Delbert', 'Delcie', 'Delena', 'Delfina', 'Delia', 'Delicia', 'Delila', 'Delilah', 'Delinda', 'Delisa', 'Dell', 'Della', 'Delma', 'Delmar', 'Delmer', 'Delmy', 'Delois', 'Deloise', 'Delora', 'Deloras', 'Delores', 'Deloris', 'Delorse', 'Delpha', 'Delphia', 'Delphine', 'Delsie', 'Delta', 'Demarcus', 'Demetra', 'Demetria', 'Demetrice', 'Demetrius', 'Dena', 'Denae', 'Deneen', 'Denese', 'Denice', 'Denis', 'Denise', 'Denisha', 'Denisse', 'Denita', 'Denna', 'Dennis', 'Dennise', 'Denny', 'Denver', 'Denyse', 'Deon', 'Deonna', 'Derek', 'Derick', 'Derrick', 'Deshawn', 'Desirae', 'Desire', 'Desiree', 'Desmond', 'Despina', 'Dessie', 'Destiny', 'Detra', 'Devin', 'Devon', 'Devona', 'Devora', 'Devorah', 'Dewayne', 'Dewey', 'Dewitt', 'Dexter', 'Dia', 'Diamond', 'Dian', 'Diana', 'Diane', 'Diann', 'Dianna', 'Dianne', 'Dick', 'Diedra', 'Diedre', 'Diego', 'Dierdre', 'Digna', 'Dillon', 'Dimple', 'Dina', 'Dinah', 'Dino', 'Dinorah', 'Dion', 'Dione', 'Dionna', 'Dionne', 'Dirk', 'Divina', 'Dixie', 'Dodie', 'Dollie', 'Dolly', 'Dolores', 'Doloris', 'Domenic', 'Domenica', 'Dominga', 'Domingo', 'Dominic', 'Dominica', 'Dominick', 'Dominique', 'Dominque', 'Domitila', 'Domonique', 'Don', 'Dona', 'Donald', 'Donella', 'Donetta', 'Donette', 'Dong', 'Donita', 'Donn', 'Donna', 'Donnell', 'Donnetta', 'Donnette', 'Donnie', 'Donny', 'Donovan', 'Donte', 'Donya', 'Dora', 'Dorathy', 'Dorcas', 'Doreatha', 'Doreen', 'Dorene', 'Doretha', 'Dorethea', 'Doretta', 'Dori', 'Doria', 'Dorian', 'Dorie', 'Dorinda', 'Dorine', 'Doris', 'Dorla', 'Dorotha', 'Dorothea', 'Dorothy', 'Dorris', 'Dorsey', 'Dortha', 'Dorthea', 'Dorthey', 'Dorthy', 'Dot', 'Dottie', 'Dotty', 'Doug', 'Douglas', 'Douglass', 'Dovie', 'Doyle', 'Dreama', 'Drema', 'Drew', 'Drucilla', 'Drusilla', 'Duane', 'Dudley', 'Dulce', 'Dulcie', 'Duncan', 'Dung', 'Dusti', 'Dustin', 'Dusty', 'Dwain', 'Dwana', 'Dwayne', 'Dwight', 'Dyan', 'Dylan', 'Earl', 'Earle', 'Earlean', 'Earleen', 'Earlene', 'Earlie', 'Earline', 'Earnest', 'Earnestine', 'Eartha', 'Easter', 'Eboni', 'Ebonie', 'Ebony', 'Echo', 'Ed', 'Eda', 'Edda', 'Eddie', 'Eddy', 'Edelmira', 'Eden', 'Edgar', 'Edgardo', 'Edie', 'Edison', 'Edith', 'Edmond', 'Edmund', 'Edmundo', 'Edna', 'Edra', 'Edris', 'Eduardo', 'Edward', 'Edwardo', 'Edwin', 'Edwina', 'Edyth', 'Edythe', 'Effie', 'Efrain', 'Efren', 'Ehtel', 'Eileen', 'Eilene', 'Ela', 'Eladia', 'Elaina', 'Elaine', 'Elana', 'Elane', 'Elanor', 'Elayne', 'Elba', 'Elbert', 'Elda', 'Elden', 'Eldon', 'Eldora', 'Eldridge', 'Eleanor', 'Eleanora', 'Eleanore', 'Elease', 'Elena', 'Elene', 'Eleni', 'Elenor', 'Elenora', 'Elenore', 'Eleonor', 'Eleonora', 'Eleonore', 'Elfreda', 'Elfrieda', 'Elfriede', 'Eli', 'Elia', 'Eliana', 'Elias', 'Elicia', 'Elida', 'Elidia', 'Elijah', 'Elin', 'Elina', 'Elinor', 'Elinore', 'Elisa', 'Elisabeth', 'Elise', 'Eliseo', 'Elisha', 'Elissa', 'Eliz', 'Eliza', 'Elizabet', 'Elizabeth', 'Elizbeth', 'Elizebeth', 'Elke', 'Ella', 'Ellamae', 'Ellan', 'Ellen', 'Ellena', 'Elli', 'Ellie', 'Elliot', 'Elliott', 'Ellis', 'Ellsworth', 'Elly', 'Ellyn', 'Elma', 'Elmer', 'Elmira', 'Elmo', 'Elna', 'Elnora', 'Elodia', 'Elois', 'Eloisa', 'Eloise', 'Elouise', 'Eloy', 'Elroy', 'Elsa', 'Else', 'Elsie', 'Elsy', 'Elton', 'Elva', 'Elvera', 'Elvia', 'Elvie', 'Elvin', 'Elvina', 'Elvira', 'Elvis', 'Elwanda', 'Elwood', 'Elyse', 'Elza', 'Ema', 'Emanuel', 'Emelda', 'Emelia', 'Emelina', 'Emeline', 'Emely', 'Emerald', 'Emerita', 'Emerson', 'Emery', 'Emiko', 'Emil', 'Emile', 'Emilee', 'Emilia', 'Emilie', 'Emilio', 'Emily', 'Emma', 'Emmaline', 'Emmanuel', 'Emmett', 'Emmie', 'Emmitt', 'Emmy', 'Emogene', 'Emory', 'Ena', 'Enda', 'Enedina', 'Eneida', 'Enid', 'Enoch', 'Enola_Gay', 'Enrique', 'Enriqueta', 'Epifania', 'Era', 'Erasmo', 'Eric', 'Erica', 'Erich', 'Erick', 'Ericka', 'Erik', 'Erika', 'Erin', 'Erinn', 'Erlene', 'Erlinda', 'Erline', 'Erma', 'Ermelinda', 'Erminia', 'Erna', 'Ernest', 'Ernestina', 'Ernestine', 'Ernesto', 'Ernie', 'Errol', 'Ervin', 'Erwin', 'Eryn', 'Esmeralda', 'Esperanza', 'Essie', 'Esta', 'Esteban', 'Estefana', 'Estela', 'Estell', 'Estella', 'Estelle', 'Ester', 'Esther', 'Estrella', 'Etha', 'Ethan', 'Ethel', 'Ethelene', 'Ethelyn', 'Ethyl', 'Etsuko', 'Etta', 'Ettie', 'Eufemia', 'Eugena', 'Eugene', 'Eugenia', 'Eugenie', 'Eugenio', 'Eula', 'Eulah', 'Eulalia', 'Eun', 'Euna', 'Eunice', 'Eura', 'Eusebia', 'Eusebio', 'Eustolia', 'Eva', 'Evalyn', 'Evan', 'Evangelina', 'Evangeline', 'Eve', 'Evelia', 'Evelin', 'Evelina', 'Eveline', 'Evelyn', 'Evelyne', 'Evelynn', 'Everett', 'Everette', 'Evette', 'Evia', 'Evie', 'Evita', 'Evon', 'Evonne', 'Ewa', 'Exie', 'Ezekiel', 'Ezequiel', 'Ezra', 'Fabian', 'Fabiola', 'Fae', 'Fairy', 'Faith', 'Fallon', 'Fannie', 'Fanny', 'Farah', 'Farrah', 'Fatima', 'Fatimah', 'Faustina', 'Faustino', 'Fausto', 'Faviola', 'Fawn', 'Fay', 'Faye', 'Fe', 'Federico', 'Felecia', 'Felica', 'Felice', 'Felicia', 'Felicidad', 'Felicita', 'Felicitas', 'Felipa', 'Felipe', 'Felisa', 'Felisha', 'Felix', 'Felton', 'Ferdinand', 'Fermin', 'Fermina', 'Fern', 'Fernanda', 'Fernande', 'Fernando', 'Ferne', 'Fidel', 'Fidela', 'Fidelia', 'Filiberto', 'Filomena', 'Fiona', 'Flavia', 'Fleta', 'Fletcher', 'Flo', 'Flor', 'Flora', 'Florance', 'Florence', 'Florencia', 'Florencio', 'Florene', 'Florentina', 'Florentino', 'Floretta', 'Floria', 'Florida', 'Florinda', 'Florine', 'Florrie', 'Flossie', 'Floy', 'Floyd', 'Fonda', 'Forest', 'Forrest', 'Foster', 'Fran', 'France', 'Francene', 'Frances', 'Francesca', 'Francesco', 'Franchesca', 'Francie', 'Francina', 'Francine', 'Francis', 'Francisca', 'Francisco', 'Francoise', 'Frank', 'Frankie', 'Franklin', 'Franklyn', 'Fransisca', 'Fred', 'Freda', 'Fredda', 'Freddie', 'Freddy', 'Frederic', 'Frederica', 'Frederick', 'Fredericka', 'Fredia', 'Fredric', 'Fredrick', 'Fredricka', 'Freeda', 'Freeman', 'Freida', 'Frida', 'Frieda', 'Fritz', 'Fumiko', 'Gabriel', 'Gabriela', 'Gabriele', 'Gabriella', 'Gabrielle', 'Gail', 'Gala', 'Gale', 'Galen', 'Galina', 'Garfield', 'Garland', 'Garnet', 'Garnett', 'Garret', 'Garrett', 'Garry', 'Garth', 'Gary', 'Gaston', 'Gavin', 'Gay', 'Gaye', 'Gayla', 'Gayle', 'Gaylene', 'Gaylord', 'Gaynell', 'Gaynelle', 'Gearldine', 'Gema', 'Gemma', 'Gena', 'Genaro', 'Gene', 'Genesis', 'Geneva', 'Genevie', 'Genevieve', 'Genevive', 'Genia', 'Genie', 'Genna', 'Gennie', 'Genny', 'Genoveva', 'Geoffrey', 'Georgann', 'George', 'Georgeann', 'Georgeanna', 'Georgene', 'Georgetta', 'Georgette', 'Georgia', 'Georgiana', 'Georgiann', 'Georgianna', 'Georgianne', 'Georgie', 'Georgina', 'Georgine', 'Gerald', 'Geraldine', 'Geraldo', 'Geralyn', 'Gerard', 'Gerardo', 'Gerda', 'Geri', 'Germaine', 'German', 'Gerri', 'Gerry', 'Gertha', 'Gertie', 'Gertrud', 'Gertrude', 'Gertrudis', 'Gertude', 'Ghislaine', 'Gia', 'Gianna', 'Gidget', 'Gigi', 'Gil', 'Gilbert', 'Gilberte', 'Gilberto', 'Gilda', 'Gillian', 'Gilma', 'Gina', 'Ginette', 'Ginger', 'Ginny', 'Gino', 'Giovanna', 'Giovanni', 'Gisela', 'Gisele', 'Giselle', 'Gita', 'Giuseppe', 'Giuseppina', 'Gladis', 'Glady', 'Gladys', 'Glayds', 'Glen', 'Glenda', 'Glendora', 'Glenn', 'Glenna', 'Glennie', 'Glennis', 'Glinda', 'Gloria', 'Glory', 'Glynda', 'Glynis', 'Golda', 'Golden', 'Goldie', 'Gonzalo', 'Gordon', 'Grace', 'Gracia', 'Gracie', 'Graciela', 'Grady', 'Graham', 'Graig', 'Grant', 'Granville', 'Grayce', 'Grazyna', 'Greg', 'Gregg', 'Gregoria', 'Gregorio', 'Gregory', 'Greta', 'Gretchen', 'Gretta', 'Gricelda', 'Grisel', 'Griselda', 'Grover', 'Guadalupe', 'Gudrun', 'Guillermina', 'Guillermo', 'Gus', 'Gussie', 'Gustavo', 'Guy', 'Gwen', 'Gwenda', 'Gwendolyn', 'Gwenn', 'Gwyn', 'Gwyneth', 'Ha', 'Hae', 'Hai', 'Hailey', 'Hal', 'Haley', 'Halina', 'Halley', 'Hallie', 'Han', 'Hana', 'Hang', 'Hanh', 'Hank', 'Hanna', 'Hannah', 'Hannelore', 'Hans', 'Harlan', 'Harland', 'Harley', 'Harmony', 'Harold', 'Harriet', 'Harriett', 'Harriette', 'Harris', 'Harrison', 'Harry', 'Harvey', 'Hassan', 'Hassie', 'Hattie', 'Haydee', 'Hayden', 'Hayley', 'Haywood', 'Hazel', 'Heath', 'Heather', 'Hector', 'Hedwig', 'Hedy', 'Hee', 'Heide', 'Heidi', 'Heidy', 'Heike', 'Helaine', 'Helen', 'Helena', 'Helene', 'Helga', 'Hellen', 'Henrietta', 'Henriette', 'Henry', 'Herb', 'Herbert', 'Heriberto', 'Herlinda', 'Herma', 'Herman', 'Hermelinda', 'Hermila', 'Hermina', 'Hermine', 'Herminia', 'Herschel', 'Hershel', 'Herta', 'Hertha', 'Hester', 'Hettie', 'Hiedi', 'Hien', 'Hilaria', 'Hilario', 'Hilary', 'Hilda', 'Hilde', 'Hildegard', 'Hildegarde', 'Hildred', 'Hillary', 'Hilma', 'Hilton', 'Hipolito', 'Hiram', 'Hiroko', 'Hisako', 'Hoa', 'Hobert', 'Holley', 'Holli', 'Hollie', 'Hollis', 'Holly', 'Homer', 'Honey', 'Hong', 'Hope', 'Horace', 'Horacio', 'Hortencia', 'Hortense', 'Hortensia', 'Hosea', 'Houston', 'Howard', 'Hoyt', 'Hsiu', 'Hubert', 'Hue', 'Huey', 'Hugh', 'Hugo', 'Hui', 'Hulda', 'Humberto', 'Hung', 'Hunter', 'Huong', 'Hwa', 'Hyacinth', 'Hye', 'Hyman', 'Hyo', 'Hyon', 'Hyun', 'Ian', 'Ida', 'Idalia', 'Idell', 'Idella', 'Iesha', 'Ignacia', 'Ignacio', 'Ike', 'Ila', 'Ilana', 'Ilda', 'Ileana', 'Ileen', 'Ilene', 'Iliana', 'Illa', 'Ilona', 'Ilse', 'Iluminada', 'Ima', 'Imelda', 'Imogene', 'In', 'Ina', 'India', 'Indira', 'Inell', 'Ines', 'Inez', 'Inga', 'Inge', 'Ingeborg', 'Inger', 'Ingrid', 'Inocencia', 'Iola', 'Iona', 'Ione', 'Ira', 'Iraida', 'Irena', 'Irene', 'Irina', 'Iris', 'Irish', 'Irma', 'Irmgard', 'Irvin', 'Irving', 'Irwin', 'Isa', 'Isaac', 'Isabel', 'Isabell', 'Isabella', 'Isabelle', 'Isadora', 'Isaiah', 'Isaias', 'Isaura', 'Isela', 'Isiah', 'Isidra', 'Isidro', 'Isis', 'Ismael', 'Isobel', 'Israel', 'Isreal', 'Issac', 'Iva', 'Ivan', 'Ivana', 'Ivelisse', 'Ivette', 'Ivey', 'Ivonne', 'Ivory', 'Ivy', 'Izetta', 'Izola', 'Ja', 'Jacalyn', 'Jacelyn', 'Jacinda', 'Jacinta', 'Jacinto', 'Jack', 'Jackeline', 'Jackelyn', 'Jacki', 'Jackie', 'Jacklyn', 'Jackqueline', 'Jackson', 'Jaclyn', 'Jacob', 'Jacqualine', 'Jacque', 'Jacquelin', 'Jacqueline', 'Jacquelyn', 'Jacquelyne', 'Jacquelynn', 'Jacques', 'Jacquetta', 'Jacqui', 'Jacquie', 'Jacquiline', 'Jacquline', 'Jacqulyn', 'Jada', 'Jade', 'Jadwiga', 'Jae', 'Jaime', 'Jaimee', 'Jaimie', 'Jake', 'Jaleesa', 'Jalisa', 'Jama', 'Jamaal', 'Jamal', 'Jamar', 'Jame', 'Jamee', 'Jamel', 'James', 'Jamey', 'Jami', 'Jamie', 'Jamika', 'Jamila', 'Jamison', 'Jammie', 'Jan', 'Jana', 'Janae', 'Janay', 'Jane', 'Janean', 'Janee', 'Janeen', 'Janel', 'Janell', 'Janella', 'Janelle', 'Janene', 'Janessa', 'Janet', 'Janeth', 'Janett', 'Janetta', 'Janette', 'Janey', 'Jani', 'Janice', 'Janie', 'Janiece', 'Janina', 'Janine', 'Janis', 'Janise', 'Janita', 'Jann', 'Janna', 'Jannet', 'Jannette', 'Jannie', 'January', 'Janyce', 'Jaqueline', 'Jaquelyn', 'Jared', 'Jarod', 'Jarred', 'Jarrett', 'Jarrod', 'Jarvis', 'Jasmin', 'Jasmine', 'Jason', 'Jasper', 'Jaunita', 'Javier', 'Jay', 'Jaye', 'Jayme', 'Jaymie', 'Jayna', 'Jayne', 'Jayson', 'Jazmin', 'Jazmine', 'Jc', 'Jean', 'Jeana', 'Jeane', 'Jeanelle', 'Jeanene', 'Jeanett', 'Jeanetta', 'Jeanette', 'Jeanice', 'Jeanie', 'Jeanine', 'Jeanmarie', 'Jeanna', 'Jeanne', 'Jeannetta', 'Jeannette', 'Jeannie', 'Jeannine', 'Jed', 'Jeff', 'Jefferey', 'Jefferson', 'Jeffery', 'Jeffie', 'Jeffrey', 'Jeffry', 'Jen', 'Jena', 'Jenae', 'Jene', 'Jenee', 'Jenell', 'Jenelle', 'Jenette', 'Jeneva', 'Jeni', 'Jenice', 'Jenifer', 'Jeniffer', 'Jenine', 'Jenise', 'Jenna', 'Jennefer', 'Jennell', 'Jennette', 'Jenni', 'Jennie', 'Jennifer', 'Jenniffer', 'Jennine', 'Jenny', 'Jerald', 'Jeraldine', 'Jeramy', 'Jere', 'Jeremiah', 'Jeremy', 'Jeri', 'Jerica', 'Jerilyn', 'Jerlene', 'Jermaine', 'Jerold', 'Jerome', 'Jeromy', 'Jerrell', 'Jerri', 'Jerrica', 'Jerrie', 'Jerrod', 'Jerrold', 'Jerry', 'Jesenia', 'Jesica', 'Jess', 'Jesse', 'Jessenia', 'Jessi', 'Jessia', 'Jessica', 'Jessie', 'Jessika', 'Jestine', 'Jesus', 'Jesusa', 'Jesusita', 'Jetta', 'Jettie', 'Jewel', 'Jewell', 'Ji', 'Jill', 'Jillian', 'Jim', 'Jimmie', 'Jimmy', 'Jin', 'Jina', 'Jinny', 'Jo', 'Joan', 'Joana', 'Joane', 'Joanie', 'Joann', 'Joanna', 'Joanne', 'Joannie', 'Joaquin', 'Joaquina', 'Jocelyn', 'Jodee', 'Jodi', 'Jodie', 'Jody', 'Joe', 'Joeann', 'Joel', 'Joella', 'Joelle', 'Joellen', 'Joesph', 'Joetta', 'Joette', 'Joey', 'Johana', 'Johanna', 'Johanne', 'John', 'Johna', 'Johnathan', 'Johnathon', 'Johnetta', 'Johnette', 'Johnie', 'Johnna', 'Johnnie', 'Johnny', 'Johnsie', 'Johnson', 'Joi', 'Joie', 'Jolanda', 'Joleen', 'Jolene', 'Jolie', 'Joline', 'Jolyn', 'Jolynn', 'Jon', 'Jona', 'Jonah', 'Jonas', 'Jonathan', 'Jonathon', 'Jone', 'Jonell', 'Jonelle', 'Jong', 'Joni', 'Jonie', 'Jonna', 'Jonnie', 'Jordan', 'Jordon', 'Jorge', 'Jose', 'Josef', 'Josefa', 'Josefina', 'Josefine', 'Joselyn', 'Joseph', 'Josephina', 'Josephine', 'Josette', 'Josh', 'Joshua', 'Josiah', 'Josie', 'Joslyn', 'Jospeh', 'Josphine', 'Josue', 'Jovan', 'Jovita', 'Joy', 'Joya', 'Joyce', 'Joycelyn', 'Joye', 'Juan', 'Juana', 'Juanita', 'Jude', 'Judi', 'Judie', 'Judith', 'Judson', 'Judy', 'Jule', 'Julee', 'Julene', 'Jules', 'Juli', 'Julia', 'Julian', 'Juliana', 'Juliane', 'Juliann', 'Julianna', 'Julianne', 'Julie', 'Julieann', 'Julienne', 'Juliet', 'Julieta', 'Julietta', 'Juliette', 'Julio', 'Julissa', 'Julius', 'June', 'Jung', 'Junie', 'Junior', 'Junita', 'Junko', 'Justa', 'Justin', 'Justina', 'Justine', 'Jutta', 'Ka', 'Kacey', 'Kaci', 'Kacie', 'Kacy', 'Kai', 'Kaila', 'Kaitlin', 'Kaitlyn', 'Kala', 'Kaleigh', 'Kaley', 'Kali', 'Kallie', 'Kalyn', 'Kam', 'Kamala', 'Kami', 'Kamilah', 'Kandace', 'Kandi', 'Kandice', 'Kandis', 'Kandra', 'Kandy', 'Kanesha', 'Kanisha', 'Kara', 'Karan', 'Kareem', 'Kareen', 'Karen', 'Karena', 'Karey', 'Kari', 'Karie', 'Karima', 'Karin', 'Karina', 'Karine', 'Karisa', 'Karissa', 'Karl', 'Karla', 'Karleen', 'Karlene', 'Karly', 'Karlyn', 'Karma', 'Karmen', 'Karol', 'Karole', 'Karoline', 'Karolyn', 'Karon', 'Karren', 'Karri', 'Karrie', 'Karry', 'Kary', 'Karyl', 'Karyn', 'Kasandra', 'Kasey', 'Kasha', 'Kasi', 'Kasie', 'Kassandra', 'Kassie', 'Kate', 'Katelin', 'Katelyn', 'Katelynn', 'Katerine', 'Kathaleen', 'Katharina', 'Katharine', 'Katharyn', 'Kathe', 'Katheleen', 'Katherin', 'Katherina', 'Katherine', 'Kathern', 'Katheryn', 'Kathey', 'Kathi', 'Kathie', 'Kathleen', 'Kathlene', 'Kathline', 'Kathlyn', 'Kathrin', 'Kathrine', 'Kathryn', 'Kathryne', 'Kathy', 'Kathyrn', 'Kati', 'Katia', 'Katie', 'Katina', 'Katlyn', 'Katrice', 'Katrina', 'Kattie', 'Katy', 'Kay', 'Kayce', 'Kaycee', 'Kaye', 'Kayla', 'Kaylee', 'Kayleen', 'Kayleigh', 'Kaylene', 'Kazuko', 'Kecia', 'Keeley', 'Keely', 'Keena', 'Keenan', 'Keesha', 'Keiko', 'Keila', 'Keira', 'Keisha', 'Keith', 'Keitha', 'Keli', 'Kelle', 'Kellee', 'Kelley', 'Kelli', 'Kellie', 'Kelly', 'Kellye', 'Kelsey', 'Kelsi', 'Kelsie', 'Kelvin', 'Kemberly', 'Ken', 'Kena', 'Kenda', 'Kendal', 'Kendall', 'Kendra', 'Kendrick', 'Keneth', 'Kenia', 'Kenisha', 'Kenna', 'Kenneth', 'Kennith', 'Kenny', 'Kent', 'Kenton', 'Kenya', 'Kenyatta', 'Kenyetta', 'Kera', 'Keren', 'Keri', 'Kermit', 'Kerri', 'Kerrie', 'Kerry', 'Kerstin', 'Kesha', 'Keshia', 'Keturah', 'Keva', 'Keven', 'Kevin', 'Khadijah', 'Khalilah', 'Kia', 'Kiana', 'Kiara', 'Kiera', 'Kiersten', 'Kiesha', 'Kieth', 'Kiley', 'Kim', 'Kimber', 'Kimberely', 'Kimberlee', 'Kimberley', 'Kimberli', 'Kimberlie', 'Kimberly', 'Kimbery', 'Kimbra', 'Kimi', 'Kimiko', 'Kina', 'Kindra', 'King', 'Kip', 'Kira', 'Kirby', 'Kirk', 'Kirsten', 'Kirstie', 'Kirstin', 'Kisha', 'Kit', 'Kittie', 'Kitty', 'Kiyoko', 'Kizzie', 'Kizzy', 'Klara', 'Korey', 'Kori', 'Kortney', 'Kory', 'Kourtney', 'Kraig', 'Kris', 'Krishna', 'Krissy', 'Krista', 'Kristal', 'Kristan', 'Kristeen', 'Kristel', 'Kristen', 'Kristi', 'Kristian', 'Kristie', 'Kristin', 'Kristina', 'Kristine', 'Kristle', 'Kristofer', 'Kristopher', 'Kristy', 'Kristyn', 'Krysta', 'Krystal', 'Krysten', 'Krystin', 'Krystina', 'Krystle', 'Krystyna', 'Kum', 'Kurt', 'Kurtis', 'Kyla', 'Kyle', 'Kylee', 'Kylie', 'Kym', 'Kymberly', 'Kyoko', 'Kyong', 'Kyra', 'Kyung', 'Lacey', 'Lachelle', 'Laci', 'Lacie', 'Lacresha', 'Lacy', 'Ladawn', 'Ladonna', 'Lady', 'Lael', 'Lahoma', 'Lai', 'Laila', 'Laine', 'Lajuana', 'Lakeesha', 'Lakeisha', 'Lakendra', 'Lakenya', 'Lakesha', 'Lakeshia', 'Lakia', 'Lakiesha', 'Lakisha', 'Lakita', 'Lala', 'Lamar', 'Lamonica', 'Lamont', 'Lan', 'Lana', 'Lance', 'Landon', 'Lane', 'Lanell', 'Lanelle', 'Lanette', 'Lang', 'Lani', 'Lanie', 'Lanita', 'Lannie', 'Lanny', 'Lanora', 'Laquanda', 'Laquita', 'Lara', 'Larae', 'Laraine', 'Laree', 'Larhonda', 'Larisa', 'Larissa', 'Larita', 'Laronda', 'Larraine', 'Larry', 'Larue', 'Lasandra', 'Lashanda', 'Lashandra', 'Lashaun', 'Lashaunda', 'Lashawn', 'Lashawna', 'Lashawnda', 'Lashay', 'Lashell', 'Lashon', 'Lashonda', 'Lashunda', 'Lasonya', 'Latanya', 'Latarsha', 'Latasha', 'Latashia', 'Latesha', 'Latia', 'Laticia', 'Latina', 'Latisha', 'Latonia', 'Latonya', 'Latoria', 'Latosha', 'Latoya', 'Latoyia', 'Latrice', 'Latricia', 'Latrina', 'Latrisha', 'Launa', 'Laura', 'Lauralee', 'Lauran', 'Laure', 'Laureen', 'Laurel', 'Lauren', 'Laurena', 'Laurence', 'Laurene', 'Lauretta', 'Laurette', 'Lauri', 'Laurice', 'Laurie', 'Laurinda', 'Laurine', 'Lauryn', 'Lavada', 'Lavelle', 'Lavenia', 'Lavera', 'Lavern', 'Laverna', 'Laverne', 'Laveta', 'Lavette', 'Lavina', 'Lavinia', 'Lavon', 'Lavona', 'Lavonda', 'Lavone', 'Lavonia', 'Lavonna', 'Lavonne', 'Lawana', 'Lawanda', 'Lawanna', 'Lawerence', 'Lawrence', 'Layla', 'Layne', 'Lazaro', 'Le', 'Lea', 'Leah', 'Lean', 'Leana', 'Leandra', 'Leandro', 'Leann', 'Leanna', 'Leanne', 'Leanora', 'Leatha', 'Leatrice', 'Lecia', 'Leda', 'Lee', 'Leeann', 'Leeanna', 'Leeanne', 'Leena', 'Leesa', 'Leia', 'Leida', 'Leif', 'Leigh', 'Leigha', 'Leighann', 'Leila', 'Leilani', 'Leisa', 'Leisha', 'Lekisha', 'Lela', 'Lelah', 'Leland', 'Lelia', 'Lemuel', 'Len', 'Lena', 'Lenard', 'Lenita', 'Lenna', 'Lennie', 'Lenny', 'Lenora', 'Lenore', 'Leo', 'Leola', 'Leoma', 'Leon', 'Leona', 'Leonard', 'Leonarda', 'Leonardo', 'Leone', 'Leonel', 'Leonia', 'Leonida', 'Leonie', 'Leonila', 'Leonor', 'Leonora', 'Leonore', 'Leontine', 'Leopoldo', 'Leora', 'Leota', 'Lera', 'Leroy', 'Les', 'Lesa', 'Lesha', 'Lesia', 'Leslee', 'Lesley', 'Lesli', 'Leslie', 'Lessie', 'Lester', 'Leta', 'Letha', 'Leticia', 'Letisha', 'Letitia', 'Lettie', 'Letty', 'Levi_Tation', 'Lewis', 'Lexie', 'Lezlie', 'Li', 'Lia', 'Liana', 'Liane', 'Lianne', 'Libbie', 'Libby', 'Liberty', 'Librada', 'Lida', 'Lidia', 'Lien', 'Lieselotte', 'Ligia', 'Lila', 'Lili', 'Lilia', 'Lilian', 'Liliana', 'Lilla', 'Lilli', 'Lillia', 'Lilliam', 'Lillian', 'Lilliana', 'Lillie', 'Lilly', 'Lily', 'Lin', 'Lina', 'Lincoln', 'Linda', 'Lindsay', 'Lindsey', 'Lindsy', 'Lindy', 'Linette', 'Ling', 'Linh', 'Linn', 'Linnea', 'Linnie', 'Lino', 'Linsey', 'Linwood', 'Lionel', 'Lisa', 'Lisabeth', 'Lisandra', 'Lisbeth', 'Lise', 'Lisette', 'Lisha', 'Lissa', 'Lissette', 'Lita', 'Livia', 'Liz', 'Liza', 'Lizabeth', 'Lizbeth', 'Lizeth', 'Lizette', 'Lizzette', 'Lizzie', 'Lloyd', 'Loan', 'Logan', 'Loida', 'Lois', 'Loise', 'Lola', 'Lolita', 'Loma', 'Lon', 'Lona', 'Londa', 'Long', 'Loni', 'Lonna', 'Lonnie', 'Lonny', 'Lora', 'Loraine', 'Loralee', 'Lore', 'Lorean', 'Loree', 'Loreen', 'Lorelei', 'Loren', 'Lorena', 'Lorene', 'Lorenza', 'Lorenzo', 'Loreta', 'Loretta', 'Lorette', 'Lori', 'Loria', 'Loriann', 'Lorie', 'Lorilee', 'Lorina', 'Lorinda', 'Lorine', 'Loris', 'Lorita', 'Lorna', 'Lorraine', 'Lorretta', 'Lorri', 'Lorriane', 'Lorrie', 'Lorrine', 'Lory', 'Lottie', 'Lou', 'Louann', 'Louanne', 'Louella', 'Louetta', 'Louie', 'Louis', 'Louisa', 'Louise', 'Loura', 'Lourdes', 'Lourie', 'Louvenia', 'Love', 'Lovella', 'Lovetta', 'Lovie', 'Lowell', 'Loyce', 'Loyd', 'Lu', 'Luana', 'Luann', 'Luanna', 'Luanne', 'Luba', 'Lucas', 'Luci', 'Lucia', 'Luciana', 'Luciano', 'Lucie', 'Lucien', 'Lucienne', 'Lucila', 'Lucile', 'Lucilla', 'Lucille', 'Lucina', 'Lucinda', 'Lucio', 'Lucius', 'Lucrecia', 'Lucretia', 'Lucy', 'Ludie', 'Ludivina', 'Lue', 'Luella', 'Luetta', 'Luigi', 'Luis', 'Luisa', 'Luise', 'Luke', 'Lula', 'Lulu', 'Luna', 'Lupe', 'Lupita', 'Lura', 'Lurlene', 'Lurline', 'Luther', 'Luvenia', 'Luz', 'Lyda', 'Lydia', 'Lyla', 'Lyle', 'Lyman', 'Lyn', 'Lynda', 'Lyndia', 'Lyndon', 'Lyndsay', 'Lyndsey', 'Lynell', 'Lynelle', 'Lynetta', 'Lynette', 'Lynn', 'Lynna', 'Lynne', 'Lynnette', 'Lynsey', 'Lynwood', 'Ma', 'Mabel', 'Mabelle', 'Mable', 'Mac', 'Machelle', 'Macie', 'Mack', 'Mackenzie', 'Macy', 'Madalene', 'Madaline', 'Madalyn', 'Maddie', 'Madelaine', 'Madeleine', 'Madelene', 'Madeline', 'Madelyn', 'Madge', 'Madie', 'Madison', 'Madlyn', 'Madonna', 'Mae', 'Maegan', 'Mafalda', 'Magali', 'Magaly', 'Magan', 'Magaret', 'Magda', 'Magdalen', 'Magdalena', 'Magdalene', 'Magen', 'Maggie', 'Magnolia', 'Mahalia', 'Mai', 'Maia', 'Maida', 'Maile', 'Maira', 'Maire', 'Maisha', 'Maisie', 'Major', 'Majorie', 'Makeda', 'Malcolm', 'Malcom', 'Malena', 'Malia', 'Malik', 'Malika', 'Malinda', 'Malisa', 'Malissa', 'Malka', 'Mallie', 'Mallory', 'Malorie', 'Malvina', 'Mamie', 'Mammie', 'Man', 'Mana', 'Manda', 'Mandi', 'Mandie', 'Mandy', 'Manie', 'Manual', 'Manuel', 'Manuela', 'Many', 'Mao', 'Maple', 'Mara', 'Maragaret', 'Maragret', 'Maranda', 'Marc', 'Marcel', 'Marcela', 'Marcelene', 'Marcelina', 'Marceline', 'Marcelino', 'Marcell', 'Marcella', 'Marcelle', 'Marcellus', 'Marcelo', 'Marcene', 'Marchelle', 'Marci', 'Marcia', 'Marcie', 'Marco', 'Marcos', 'Marcus', 'Marcy', 'Mardell', 'Maren', 'Marg', 'Margaret', 'Margareta', 'Margarete', 'Margarett', 'Margaretta', 'Margarette', 'Margarita', 'Margarite', 'Margarito', 'Margart', 'Marge', 'Margene', 'Margeret', 'Margert', 'Margery', 'Marget', 'Margherita', 'Margie', 'Margit', 'Margo', 'Margorie', 'Margot', 'Margret', 'Margrett', 'Marguerita', 'Marguerite', 'Margurite', 'Margy', 'Marhta', 'Mari', 'Maria', 'Mariah', 'Mariam', 'Marian', 'Mariana', 'Marianela', 'Mariann', 'Marianna', 'Marianne', 'Mariano', 'Maribel', 'Maribeth', 'Marica', 'Maricela', 'Maricruz', 'Marie', 'Mariel', 'Mariela', 'Mariella', 'Marielle', 'Marietta', 'Mariette', 'Mariko', 'Marilee', 'Marilou', 'Marilu', 'Marilyn', 'Marilynn', 'Marin', 'Marina', 'Marinda', 'Marine', 'Mario', 'Marion', 'Maris', 'Marisa', 'Marisela', 'Marisha', 'Marisol', 'Marissa', 'Marita', 'Maritza', 'Marivel', 'Marjorie', 'Marjory', 'Mark', 'Marketta', 'Markita', 'Markus', 'Marla', 'Marlana', 'Marleen', 'Marlen', 'Marlena', 'Marlene', 'Marlin', 'Marline', 'Marlo', 'Marlon', 'Marlyn', 'Marlys', 'Marna', 'Marni', 'Marnie', 'Marquerite', 'Marquetta', 'Marquis', 'Marquita', 'Marquitta', 'Marry', 'Marsha', 'Marshall', 'Marta', 'Marth', 'Martha', 'Marti', 'Martin', 'Martina', 'Martine', 'Marty', 'Marva', 'Marvel', 'Marvella', 'Marvin', 'Marvis', 'Marx', 'Mary', 'Marya', 'Maryalice', 'Maryam', 'Maryann', 'Maryanna', 'Maryanne', 'Marybelle', 'Marybeth', 'Maryellen', 'Maryetta', 'Maryjane', 'Maryjo', 'Maryland', 'Marylee', 'Marylin', 'Maryln', 'Marylou', 'Marylouise', 'Marylyn', 'Marylynn', 'Maryrose', 'Masako', 'Mason', 'Matha', 'Mathew', 'Mathilda', 'Mathilde', 'Matilda', 'Matilde', 'Matt', 'Matthew', 'Mattie', 'Maud', 'Maude', 'Maudie', 'Maura', 'Maureen', 'Maurice', 'Mauricio', 'Maurine', 'Maurita', 'Mauro', 'Mavis', 'Max', 'Maxie', 'Maxima', 'Maximina', 'Maximo', 'Maxine', 'Maxwell', 'May', 'Maya', 'Maybell', 'Maybelle', 'Maye', 'Mayme', 'Maynard', 'Mayola', 'Mayra', 'Mazie', 'Mckenzie', 'Mckinley', 'Meagan', 'Meaghan', 'Mechelle', 'Meda', 'Mee', 'Meg', 'Megan', 'Meggan', 'Meghan', 'Meghann', 'Mei', 'Mel', 'Melaine', 'Melani', 'Melania', 'Melanie', 'Melany', 'Melba', 'Melda', 'Melia', 'Melida', 'Melina', 'Melinda', 'Melisa', 'Melissa', 'Melissia', 'Melita', 'Mellie', 'Mellisa', 'Mellissa', 'Melodee', 'Melodi', 'Melodie', 'Melody', 'Melonie', 'Melony', 'Melva', 'Melvin', 'Melvina', 'Melynda', 'Mendy', 'Mercedes', 'Mercedez', 'Mercy', 'Meredith', 'Meri', 'Merideth', 'Meridith', 'Merilyn', 'Merissa', 'Merle', 'Merlene', 'Merlin', 'Merlyn', 'Merna', 'Merri', 'Merrie', 'Merrilee', 'Merrill', 'Merry', 'Mertie', 'Mervin', 'Meryl', 'Meta', 'Mi', 'Mia', 'Mica', 'Micaela', 'Micah', 'Micha', 'Michael', 'Michaela', 'Michaele', 'Michal', 'Michale', 'Micheal', 'Michel', 'Michele', 'Michelina', 'Micheline', 'Michell', 'Michelle', 'Michiko', 'Mickey', 'Micki', 'Mickie', 'Miesha', 'Migdalia', 'Mignon', 'Miguel', 'Miguelina', 'Mika', 'Mikaela', 'Mike', 'Mikel', 'Miki', 'Mikki', 'Mila', 'Milagro', 'Milagros', 'Milan', 'Milda', 'Mildred', 'Miles', 'Milford', 'Milissa', 'Millard', 'Millicent', 'Millie', 'Milly', 'Milo', 'Milton', 'Mimi', 'Min', 'Mina', 'Minda', 'Mindi', 'Mindy', 'Minerva', 'Ming', 'Minh', 'Minna', 'Minnie', 'Minta', 'Miquel', 'Mira', 'Miranda', 'Mireille', 'Mirella', 'Mireya', 'Miriam', 'Mirian', 'Mirna', 'Mirta', 'Mirtha', 'Misha', 'Miss', 'Missy', 'Misti', 'Mistie', 'Misty', 'Mitch', 'Mitchel', 'Mitchell', 'Mitsue', 'Mitsuko', 'Mittie', 'Mitzi', 'Mitzie', 'Miyoko', 'Modesta', 'Modesto', 'Mohamed', 'Mohammad', 'Mohammed', 'Moira', 'Moises', 'Mollie', 'Molly', 'Mona', 'Monet', 'Monica', 'Monika', 'Monique', 'Monnie', 'Monroe', 'Monserrate', 'Monte', 'Monty', 'Moon', 'Mora', 'Morgan', 'Moriah', 'Morris', 'Morton', 'Mose', 'Moses', 'Moshe', 'Mozell', 'Mozella', 'Mozelle', 'Mui', 'Muoi', 'Muriel', 'Murray', 'My', 'Myesha', 'Myles', 'Myong', 'Myra', 'Myriam', 'Myrl', 'Myrle', 'Myrna', 'Myron', 'Myrta', 'Myrtice', 'Myrtie', 'Myrtis', 'Myrtle', 'Myung', 'Na', 'Nada', 'Nadene', 'Nadia', 'Nadine', 'Naida', 'Nakesha', 'Nakia', 'Nakisha', 'Nakita', 'Nam', 'Nan', 'Nana', 'Nancee', 'Nancey', 'Nanci', 'Nancie', 'Nancy', 'Nanette', 'Nannette', 'Nannie', 'Naoma', 'Naomi', 'Napoleon', 'Narcisa', 'Natacha', 'Natalia', 'Natalie', 'Natalya', 'Natasha', 'Natashia', 'Nathalie', 'Nathan', 'Nathanael', 'Nathanial', 'Nathaniel', 'Natisha', 'Natividad', 'Natosha', 'Neal', 'Necole', 'Ned', 'Neda', 'Nedra', 'Neely', 'Neida', 'Neil', 'Nelda', 'Nelia', 'Nelida', 'Nell', 'Nella', 'Nelle', 'Nellie', 'Nelly', 'Nelson', 'Nena', 'Nenita', 'Neoma', 'Neomi', 'Nereida', 'Nerissa', 'Nery', 'Nestor', 'Neta', 'Nettie', 'Neva', 'Nevada', 'Neville', 'Newton', 'Nga', 'Ngan', 'Ngoc', 'Nguyet', 'Nia', 'Nichelle', 'Nichol', 'Nicholas', 'Nichole', 'Nicholle', 'Nick', 'Nicki', 'Nickie', 'Nickolas', 'Nickole', 'Nicky', 'Nicol', 'Nicola', 'Nicolas', 'Nicolasa', 'Nicole', 'Nicolette', 'Nicolle', 'Nida', 'Nidia', 'Niesha', 'Nieves', 'Nigel', 'Niki', 'Nikia', 'Nikita', 'Nikki', 'Nikole', 'Nila', 'Nilda', 'Nilsa', 'Nina', 'Ninfa', 'Nisha', 'Nita', 'Noah', 'Noble', 'Nobuko', 'Noe', 'Noel', 'Noelia', 'Noella', 'Noelle', 'Noemi', 'Nohemi', 'Nola', 'Nolan', 'Noma', 'Nona', 'Nora', 'Norah', 'Norbert', 'Norberto', 'Noreen', 'Norene', 'Noriko', 'Norine', 'Norma', 'Norman', 'Normand', 'Norris', 'Nova', 'Novella', 'Nu', 'Nubia', 'Numbers', 'Nydia', 'Nyla', 'Obdulia', 'Ocie', 'Octavia', 'Octavio', 'Oda', 'Odelia', 'Odell', 'Odessa', 'Odette', 'Odilia', 'Odis', 'Ofelia', 'Ok', 'Ola', 'Olen', 'Olene', 'Oleta', 'Olevia', 'Olga', 'Olimpia', 'Olin', 'Olinda', 'Oliva', 'Olive', 'Oliver', 'Olivia', 'Ollie', 'Olympia', 'Oma', 'Omar', 'Omega', 'Omer', 'Ona', 'Oneida', 'Onie', 'Onita', 'Opal', 'Ophelia', 'Ora', 'Oralee', 'Oralia', 'Oren', 'Oretha', 'Orlando', 'Orpha', 'Orval', 'Orville', 'Oscar', 'Ossie', 'Osvaldo', 'Oswaldo', 'Otelia', 'Otha', 'Otilia', 'Otis', 'Otto', 'Ouida', 'Owen', 'Ozell', 'Ozella', 'Ozie', 'Pa', 'Pablo', 'Page', 'Paige', 'Palma', 'Palmer', 'Palmira', 'Pam', 'Pamala', 'Pamela', 'Pamelia', 'Pamella', 'Pamila', 'Pamula', 'Pandora', 'Pansy', 'Paola', 'Paris', 'Parker', 'Parthenia', 'Particia', 'Pasquale', 'Pasty', 'Pat', 'Patience_Jarrive', 'Patria', 'Patrica', 'Patrice', 'Patricia', 'Patrick', 'Patrina', 'Patsy', 'Patti', 'Pattie', 'Patty', 'Paul', 'Paula', 'Paulene', 'Pauletta', 'Paulette', 'Paulina', 'Pauline', 'Paulita', 'Paz', 'Pearl', 'Pearle', 'Pearlene', 'Pearlie', 'Pearline', 'Pearly', 'Pedro', 'Peg', 'Peggie', 'Peggy', 'Pei', 'Penelope', 'Penney', 'Penni', 'Pennie', 'Penny', 'Percy', 'Perla', 'Perry', 'Pete', 'Peter', 'Petra', 'Petrina', 'Petronila', 'Phebe', 'Phil', 'Philip', 'Phillip', 'Phillis', 'Philomena', 'Phoebe', 'Phung', 'Phuong', 'Phylicia', 'Phylis', 'Phyliss', 'Phyllis', 'Pia', 'Piedad', 'Pierre', 'Pilar', 'Ping', 'Pinkie', 'Piper', 'Pok', 'Polly', 'Porfirio', 'Porsche', 'Porsha', 'Porter', 'Portia', 'Precious', 'Preston', 'Pricilla', 'Prince', 'Princess', 'Priscila', 'Priscilla', 'Providencia', 'Prudence', 'Pura', 'Qiana', 'QUEEN', 'Queenie', 'Quentin', 'Quiana', 'Quincy', 'Quinn', 'Quintin', 'Quinton', 'Quyen', 'Rachael', 'Rachal', 'Racheal', 'Rachel', 'Rachele', 'Rachell', 'Rachelle', 'Racquel', 'Rae', 'Raeann', 'Raelene', 'Rafael', 'Rafaela', 'Raguel', 'Raina', 'Raisa', 'Raleigh', 'Ralph', 'Ramiro', 'Ramon', 'Ramona', 'Ramonita', 'Rana', 'Ranae', 'Randa', 'Randal', 'Randall', 'Randee', 'Randell', 'Randi', 'Randolph', 'Randy', 'Ranee', 'Raphael', 'Raquel', 'Rashad', 'Rasheeda', 'Rashida', 'Raul', 'Raven', 'Ray', 'Raye', 'Rayford', 'Raylene', 'Raymon', 'Raymond', 'Raymonde', 'Raymundo', 'Rayna', 'Rea', 'Reagan', 'Reanna', 'Reatha', 'Reba', 'Rebbeca', 'Rebbecca', 'Rebeca', 'Rebecca', 'Rebecka', 'Rebekah', 'Reda', 'Reed', 'Reena', 'Refugia', 'Refugio', 'Regan', 'Regena', 'Regenia', 'Reggie', 'Regina', 'Reginald', 'Regine', 'Reginia', 'Reid', 'Reiko', 'Reina', 'Reinaldo', 'Reita', 'Rema', 'Remedios', 'Remona', 'Rena', 'Renae', 'Renaldo', 'Renata', 'Renate', 'Renato', 'Renay', 'Renda', 'Rene', 'Renea', 'Renee', 'Renetta', 'Renita', 'Renna', 'Ressie', 'Reta', 'Retha', 'Retta', 'Reuben', 'Reva', 'Rex', 'Rey', 'Reyes', 'Reyna', 'Reynalda', 'Reynaldo', 'Rhea', 'Rheba', 'Rhett', 'Rhiannon', 'Rhoda', 'Rhona', 'Rhonda', 'Ria', 'Ricarda', 'Ricardo', 'Rich', 'Richard', 'Richelle', 'Richie', 'Rick', 'Rickey', 'Ricki', 'Rickie', 'Ricky', 'Rico', 'Rigoberto', 'Rikki', 'Riley', 'Rima', 'Rina', 'Risa', 'Rita', 'Riva', 'Rivka', 'Rob', 'Robbi', 'Robbie', 'Robbin', 'Robby', 'Robbyn', 'Robena', 'Robert', 'Roberta', 'Roberto', 'Robin', 'Robt', 'Robyn', 'Rocco', 'Rochel', 'Rochell', 'Rochelle', 'Rocio', 'Rocky', 'Rod', 'Roderick', 'Rodger', 'Rodney', 'Rodolfo', 'Rodrick', 'Rodrigo', 'Rogelio', 'Roger', 'Roland', 'Rolanda', 'Rolande', 'Rolando', 'Rolf', 'Rolland', 'Roma', 'Romaine', 'Roman', 'Romana', 'Romelia', 'Romeo', 'Romona', 'Ron', 'Rona', 'Ronald', 'Ronda', 'Roni', 'Ronna', 'Ronni', 'Ronnie', 'Ronny', 'Roosevelt', 'Rory', 'Rosa', 'Rosalba', 'Rosalee', 'Rosalia', 'Rosalie', 'Rosalina', 'Rosalind', 'Rosalinda', 'Rosaline', 'Rosalva', 'Rosalyn', 'Rosamaria', 'Rosamond', 'Rosana', 'Rosann', 'Rosanna', 'Rosanne', 'Rosaria', 'Rosario', 'Rosaura', 'Roscoe', 'Rose', 'Roseann', 'Roseanna', 'Roseanne', 'Roselee', 'Roselia', 'Roseline', 'Rosella', 'Roselle', 'Roselyn', 'Rosemarie', 'Rosemary', 'Rosena', 'Rosenda', 'Rosendo', 'Rosetta', 'Rosette', 'Rosia', 'Rosie', 'Rosina', 'Rosio', 'Rosita', 'Roslyn', 'Ross', 'Rossana', 'Rossie', 'Rosy', 'Rowena', 'Roxana', 'Roxane', 'Roxann', 'Roxanna', 'Roxanne', 'Roxie', 'Roxy', 'Roy', 'Royal', 'Royce', 'Rozanne', 'Rozella', 'Ruben', 'Rubi', 'Rubie', 'Rubin', 'Ruby', 'Rubye', 'Rudolf', 'Rudolph', 'Rudy', 'Rueben', 'Rufina', 'Rufus', 'Rupert', 'Russ', 'Russel', 'Russell', 'Rusty', 'Ruth', 'Rutha', 'Ruthann', 'Ruthanne', 'Ruthe', 'Ruthie', 'Ryan', 'Ryann', 'Sabina', 'Sabine', 'Sabra', 'Sabrina', 'Sacha', 'Sachiko', 'Sade', 'Sadie', 'Sadye', 'Sage', 'Sal', 'Salena', 'Salina', 'Salley', 'Sallie', 'Sally', 'Salome', 'Salvador', 'Salvatore', 'Sam', 'Samantha', 'Samara', 'Samatha', 'Samella', 'Samira', 'Sammie', 'Sammy', 'Samual', 'Samuel', 'Sana', 'Sanda', 'Sandee', 'Sandi', 'Sandie', 'Sandra', 'Sandy', 'Sanford', 'Sang', 'Sanjuana', 'Sanjuanita', 'Sanora', 'Santa', 'Santana', 'Santiago', 'Santina', 'Santo', 'Santos', 'Sara', 'Sarah', 'Sarai', 'Saran', 'Sari', 'Sarina', 'Sarita', 'Sasha', 'Saturnina', 'Sau', 'Saul', 'Saundra', 'Savanna', 'Savannah', 'Scarlet', 'Scarlett', 'Scot', 'Scott', 'Scottie', 'Scotty', 'Sean', 'Season', 'Sebastian', 'Sebrina', 'See', 'Seema', 'Selena', 'Selene', 'Selina', 'Selma', 'Sena', 'Senaida', 'September', 'Serafina', 'Serena', 'Sergio', 'Serina', 'Serita', 'Seth', 'Setsuko', 'Seymour', 'Sha', 'Shad', 'Shae', 'Shaina', 'Shakia', 'Shakira', 'Shakita', 'Shala', 'Shalanda', 'Shalon', 'Shalonda', 'Shameka', 'Shamika', 'Shan', 'Shana', 'Shanae', 'Shanda', 'Shandi', 'Shandra', 'Shane', 'Shaneka', 'Shanel', 'Shanell', 'Shanelle', 'Shani', 'Shanice', 'Shanika', 'Shaniqua', 'Shanita', 'Shanna', 'Shannan', 'Shannon', 'Shanon', 'Shanta', 'Shantae', 'Shantay', 'Shante', 'Shantel', 'Shantell', 'Shantelle', 'Shanti', 'Shaquana', 'Shaquita', 'Shara', 'Sharan', 'Sharda', 'Sharee', 'Sharell', 'Sharen', 'Shari', 'Sharice', 'Sharie', 'Sharika', 'Sharilyn', 'Sharita', 'Sharla', 'Sharleen', 'Sharlene', 'Sharmaine', 'Sharolyn', 'Sharon', 'Sharonda', 'Sharri', 'Sharron', 'Sharyl', 'Sharyn', 'Shasta', 'Shaun', 'Shauna', 'Shaunda', 'Shaunna', 'Shaunta', 'Shaunte', 'Shavon', 'Shavonda', 'Shavonne', 'Shawana', 'Shawanda', 'Shawanna', 'Shawn', 'Shawna', 'Shawnda', 'Shawnee', 'Shawnna', 'Shawnta', 'Shay', 'Shayla', 'Shayna', 'Shayne', 'Shea', 'Sheba', 'Sheena', 'Sheila', 'Sheilah', 'Shela', 'Shelba', 'Shelby', 'Sheldon', 'Shelia', 'Shella', 'Shelley', 'Shelli', 'Shellie', 'Shelly', 'Shelton', 'Shemeka', 'Shemika', 'Shena', 'Shenika', 'Shenita', 'Shenna', 'Shera', 'Sheree', 'Sherell', 'Sheri', 'Sherice', 'Sheridan', 'Sherie', 'Sherika', 'Sherill', 'Sherilyn', 'Sherise', 'Sherita', 'Sherlene', 'Sherley', 'Sherly', 'Sherlyn', 'Sherman', 'Sheron', 'Sherrell', 'Sherri', 'Sherrie', 'Sherril', 'Sherrill', 'Sherron', 'Sherry', 'Sherryl', 'Sherwood', 'Shery', 'Sheryl', 'Sheryll', 'Shiela', 'Shila', 'Shiloh', 'Shin', 'Shira', 'Shirely', 'Shirl', 'Shirlee', 'Shirleen', 'Shirlene', 'Shirley', 'Shirly', 'Shizue', 'Shizuko', 'Shon', 'Shona', 'Shonda', 'Shondra', 'Shonna', 'Shonta', 'Shoshana', 'Shu', 'Shyla', 'Sibyl', 'Sid', 'Sidney', 'Sierra', 'Signe', 'Sigrid', 'Silas', 'Silva', 'Silvana', 'Silvia', 'Sima', 'Simon', 'Simona', 'Simone', 'Simonne', 'Sina', 'Sindy', 'Siobhan', 'Sirena', 'Siu', 'Sixta', 'Skye', 'Slyvia', 'So', 'Socorro', 'Sofia', 'Soila', 'Sol', 'Solange', 'Soledad', 'Solomon', 'Somer', 'Sommer', 'Son', 'Sona', 'Sondra', 'Song', 'Sonia', 'Sonja', 'Sonny', 'Sonya', 'Soo', 'Sook', 'Soon', 'Sophia', 'Sophie', 'Soraya', 'Sparkle', 'Spencer', 'Spring', 'Stacee', 'Stacey', 'Staci', 'Stacia', 'Stacie', 'Stacy', 'Stan', 'Stanford', 'Stanley', 'Stanton', 'Star', 'Starla', 'Starr', 'Stasia', 'Stefan', 'Stefani', 'Stefania', 'Stefanie', 'Stefany', 'Steffanie', 'Stella', 'Stepanie', 'Stephaine', 'Stephan', 'Stephane', 'Stephani', 'Stephania', 'Stephanie', 'Stephany', 'Stephen', 'Stephenie', 'Stephine', 'Stephnie', 'Sterling', 'Steve', 'Steven', 'Stevie', 'Stewart', 'Stormy', 'Stuart', 'Su', 'Suanne', 'Sudie', 'Sue', 'Sueann', 'Suellen', 'Suk', 'Sulema', 'Sumiko', 'Summer', 'Sun', 'Sunday', 'Sung', 'Sunni', 'Sunny', 'Sunshine', 'Susan', 'Susana', 'Susann', 'Susanna', 'Susannah', 'Susanne', 'Susie', 'Susy', 'Suzan', 'Suzann', 'Suzanna', 'Suzanne', 'Suzette', 'Suzi', 'Suzie', 'Suzy', 'Svetlana', 'Sybil', 'Syble', 'Sydney', 'Sylvester', 'Sylvia', 'Sylvie', 'Synthia', 'Syreeta', 'Ta', 'Tabatha', 'Tabetha', 'Tabitha', 'Tad', 'Tai', 'Taina', 'Taisha', 'Tajuana', 'Takako', 'Takisha', 'Talia', 'Talisha', 'Talitha', 'Tam', 'Tama', 'Tamala', 'Tamar', 'Tamara', 'Tamatha', 'Tambra', 'Tameika', 'Tameka', 'Tamekia', 'Tamela', 'Tamera', 'Tamesha', 'Tami', 'Tamica', 'Tamie', 'Tamika', 'Tamiko', 'Tamisha', 'Tammara', 'Tammera', 'Tammi', 'Tammie', 'Tammy', 'Tamra', 'Tana', 'Tandra', 'Tandy', 'Taneka', 'Tanesha', 'Tangela', 'Tania', 'Tanika', 'Tanisha', 'Tanja', 'Tanna', 'Tanner', 'Tanya', 'Tara', 'Tarah', 'Taren', 'Tari', 'Tarra', 'Tarsha', 'Taryn', 'Tasha', 'Tashia', 'Tashina', 'Tasia', 'Tatiana', 'Tatum', 'Tatyana', 'Taunya', 'Tawana', 'Tawanda', 'Tawanna', 'Tawna', 'Tawny', 'Tawnya', 'Taylor', 'Tayna', 'Ted', 'Teddy', 'Teena', 'Tegan', 'Teisha', 'Telma', 'Temeka', 'Temika', 'Tempie', 'Temple', 'Tena', 'Tenesha', 'Tenisha', 'Tennie', 'Tennille', 'Teodora', 'Teodoro', 'Teofila', 'Tequila', 'Tera', 'Tereasa', 'Terence', 'Teresa', 'Terese', 'Teresia', 'Teresita', 'Teressa', 'Teri', 'Terica', 'Terina', 'Terisa', 'Terra', 'Terrance', 'Terrell', 'Terrence', 'Terresa', 'Terri', 'Terrie', 'Terrilyn', 'Terry', 'Tesha', 'Tess', 'Tessa', 'Tessie', 'Thad', 'Thaddeus', 'Thalia', 'Thanh', 'Thao', 'Thea', 'Theda', 'Thelma', 'Theo', 'Theodora', 'Theodore', 'Theola', 'Theresa', 'Therese', 'Theresia', 'Theressa', 'Theron', 'Thersa', 'Thi', 'Thomas', 'Thomasena', 'Thomasina', 'Thomasine', 'Thora', 'Thresa', 'Thu', 'Thurman', 'Thuy', 'Tia', 'Tiana', 'Tianna', 'Tiara', 'Tien', 'Tiera', 'Tierra', 'Tiesha', 'Tifany', 'Tiffaney', 'Tiffani', 'Tiffanie', 'Tiffany', 'Tiffiny', 'Tijuana', 'Tilda', 'Tillie', 'Tim', 'Timika', 'Timmy', 'Timothy', 'Tina', 'Tinisha', 'Tiny', 'Tisa', 'Tish', 'Tisha', 'Titus', 'Tobi', 'Tobias', 'Tobie', 'Toby', 'Toccara', 'Tod', 'Todd', 'Toi', 'Tom', 'Tomas', 'Tomasa', 'Tomeka', 'Tomi', 'Tomika', 'Tomiko', 'Tommie', 'Tommy', 'Tommye', 'Tomoko', 'Tona', 'Tonda', 'Tonette', 'Toney', 'Toni', 'Tonia', 'Tonie', 'Tonisha', 'Tonita', 'Tonja', 'Tony', 'Tonya', 'Tora', 'Tori', 'Torie', 'Torri', 'Torrie', 'Tory', 'Tosha', 'Toshia', 'Toshiko', 'Tova', 'Towanda', 'Toya', 'Tracee', 'Tracey', 'Traci', 'Tracie', 'Tracy', 'Tran', 'Trang', 'Travis', 'Treasa', 'Treena', 'Trena', 'Trent', 'Trenton', 'Tresa', 'Tressa', 'Tressie', 'Treva', 'Trevor', 'Trey', 'Tricia', 'Trina', 'Trinh', 'Trinidad', 'Trinity', 'Trish', 'Trisha', 'Trista', 'Tristan', 'Troy', 'Trudi', 'Trudie', 'Trudy', 'Trula', 'Truman', 'Tu', 'Tuan', 'Tula', 'Tuyet', 'Twana', 'Twanda', 'Twanna', 'Twila', 'Twyla', 'Ty', 'Tyesha', 'Tyisha', 'Tyler', 'Tynisha', 'Tyra', 'Tyree', 'Tyrell', 'Tyron', 'Tyrone', 'Tyson', 'Ula', 'Ulrike', 'Ulysses', 'Un', 'Una', 'Ursula', 'Usha', 'Ute', 'Vada', 'Val', 'Valarie', 'Valda', 'Valencia', 'Valene', 'Valentin', 'Valentina', 'Valentine', 'Valeri', 'Valeria', 'Valerie', 'Valery', 'Vallie', 'Valorie', 'Valrie', 'Van', 'Vance', 'Vanda', 'Vanesa', 'Vanessa', 'Vanetta', 'Vania', 'Vanita', 'Vanna', 'Vannesa', 'Vannessa', 'Vashti', 'Vasiliki', 'Vaughn', 'Veda', 'Velda', 'Velia', 'Vella', 'Velma', 'Velva', 'Velvet', 'Vena', 'Venessa', 'Venetta', 'Venice', 'Venita', 'Vennie', 'Venus', 'Veola', 'Vera', 'Verda', 'Verdell', 'Verdie', 'Verena', 'Vergie', 'Verla', 'Verlene', 'Verlie', 'Verline', 'Vern', 'Verna', 'Vernell', 'Vernetta', 'Vernia', 'Vernice', 'Vernie', 'Vernita', 'Vernon', 'Verona', 'Veronica', 'Veronika', 'Veronique', 'Versie', 'Vertie', 'Vesta', 'Veta', 'Vi', 'Vicenta', 'Vicente', 'Vickey', 'Vicki', 'Vickie', 'Vicky', 'Victor', 'Victoria', 'Victorina', 'Vida', 'Viki', 'Vikki', 'Vilma', 'Vina', 'Vince', 'Vincent', 'Vincenza', 'Vincenzo', 'Vinita', 'Vinnie', 'Viola', 'Violet', 'Violeta', 'Violette', 'Virgen', 'Virgie', 'Virgil', 'Virgilio', 'Virgina', 'Virginia', 'Vita', 'Vito', 'Viva', 'Vivan', 'Vivian', 'Viviana', 'Vivien', 'Vivienne', 'Von', 'Voncile', 'Vonda', 'Vonnie', 'Wade', 'Wai', 'Waldo', 'Walker', 'Wallace', 'Wally', 'Walter', 'Walton', 'Waltraud', 'Wan', 'Wanda', 'Waneta', 'Wanetta', 'Wanita', 'Ward', 'Warner', 'Warren', 'Wava', 'Waylon', 'Wayne', 'Wei', 'Weldon', 'Wen', 'Wendell', 'Wendi', 'Wendie', 'Wendolyn', 'Wendy', 'Wenona', 'Werner', 'Wes', 'Wesley', 'Weston', 'Whitley', 'Whitney', 'Wilber', 'Wilbert', 'Wilbur', 'Wilburn', 'Wilda', 'Wiley', 'Wilford', 'Wilfred', 'Wilfredo', 'Wilhelmina', 'Wilhemina', 'Will', 'Willa', 'Willard', 'Willena', 'Willene', 'Willetta', 'Willette', 'Willia', 'William', 'Williams', 'Willian', 'Willie', 'Williemae', 'Willis', 'Willodean', 'Willow', 'Willy', 'Wilma', 'Wilmer', 'Wilson', 'Wilton', 'Windy', 'Winford', 'Winfred', 'Winifred', 'Winnie', 'Winnifred', 'Winona', 'Winston', 'Winter', 'Wm', 'Wonda', 'Woodrow', 'Wyatt', 'Wynell', 'Wynona', 'Xavier', 'Xenia', 'Xiao', 'Xiomara', 'Xochitl', 'Xuan', 'Yadira', 'Yaeko', 'Yael', 'Yahaira', 'Yajaira', 'Yan', 'Yang', 'Yanira', 'Yasmin', 'Yasmine', 'Yasuko', 'Yee', 'Yelena', 'Yen', 'Yer', 'Yesenia', 'Yessenia', 'Yetta', 'Yevette', 'Yi', 'Ying', 'Yoko', 'Yolanda', 'Yolande', 'Yolando', 'Yolonda', 'Yon', 'Yong', 'Yoshie', 'Yoshiko', 'Youlanda', 'Young', 'Yu', 'Yuette', 'Yuk', 'Yuki', 'Yukiko', 'Yuko', 'Yulanda', 'Yun', 'Yung', 'Yuonne', 'Yuri', 'Yuriko', 'Yvette', 'Yvone', 'Yvonne', 'Zachariah', 'Zachary', 'Zachery', 'Zack', 'Zackary', 'Zada', 'Zaida', 'Zana', 'Zandra', 'Zane', 'Zelda', 'Zella', 'Zelma', 'Zena', 'Zenaida', 'Zenia', 'Zenobia', 'Zetta', 'Zina', 'Zita', 'Zoe', 'Zofia', 'Zoila', 'Zola', 'Zona', 'Zonia', 'Zora', 'Zoraida', 'Zula', 'Zulema', 'Zulma']

    # All the name already taken
    # List( (str, id) )
    AI_data['taken_name'] = list()
    # If a ship must return to portal or no
    AI_data['return_portal'] = dict()

    # ----------------------------------------------------------------#
    if log:
        # Will redirect all the print() into a txt file
        # With a log file we can analyse previous game to improve the AI
        log_file = open(log_path, 'a')
        sys.stdout = log_file

    if not error:
        # 'TURN x (y)' : where x is the current turn and y the amount of turn without damage
        line = '\n' + '*' * 25 + ' ' * 5
        line += 'TURN %s (%s)' % (turn, turn_wo_dmg)
        line += ' ' * 5 + '*' * 25 + '\n'
        print(line)
        # First display of the map to the player
        display(ships, players, info_ships, asteroids, map_width, map_height)

    # Loop on game until the end of the game
    while not over and not error:
        turn += 1

        actions = cmd(ships, players, info_ships, asteroids, map_width, map_height, turn, AI_data, connection)
        
        # First check legality of buy actions and execute buy actions
        # By doing this we avoid problem with actions on recently bought ships
        actions[0] = clean_actions([actions[0],[],[],[]], ships, info_ships, players, map_width, map_height)[0]
        ships, players = buy(info_ships, actions, ships, players)
        
        # Then clean all the actions and execute
        actions = clean_actions([[], actions[1], actions[2], actions[3]], ships, info_ships, players, map_width, map_height)
        ships = lock(actions, ships)
        ships = move(ships, actions)
        hit, ships, players = fire(actions, ships, players, info_ships)

        turn_wo_dmg = 0 if hit else turn_wo_dmg + 1

        ships, players, asteroids = grab_ore(ships, players, asteroids, info_ships)

        line = '\n' + '*' * 25 + ' ' * 5
        # 'TURN x (y)' : where x is the current turn and y the amount of turn without damage
        line += 'TURN %s (%s)' % (turn, turn_wo_dmg)
        line += ' ' * 5 + '*' * 25 + '\n'
        print(line)

        display(ships, players, info_ships, asteroids, map_width, map_height)

        # Check if game is over
        if turn_wo_dmg >= turn_wo_dmg_max:
            over = True
        for player in players:
            if player['portal_life'] <= 0:
                over = True

    end(players, turn_wo_dmg, turn_wo_dmg_max, connection)
    if log:
        # Return stdout to his default value
        sys.stdout = sys.__stdout__
        log_file.close()

        # Read the log file, then delete all the color formating
        log_file = open(log_path, 'r')
        log_text = log_file.read()
        print(log_text)
        log_text = log_text.replace(colored(' ', 'red').split(' ')[0], '')
        log_text = log_text.replace(colored(' ', 'blue').split(' ')[0], '')
        log_text = log_text.replace(colored(' ', 'magenta').split(' ')[0], '')
        log_text = log_text.replace(colored(' ', attrs=['underline']).split(' ')[0], '')
        log_text = log_text.replace(colored(' ', 'red').split(' ')[1], '')
        log_file.close()

        # Rewrite in the log file, all text without color
        log_file = open(log_path, 'w')
        log_file.write(log_text)
        log_file.close()



def start(player1, player2, path):
    """Initialize the game.

    Parameters
    ----------
    player1: name and type of first player (2-sized tuple of strings)
    player2: name and type of second player (2-sized tuple of strings)
    path: path to the config file (str)

    Returns
    -------
    players: structure containing players' informations (list of dict)
    asteroids: structure containing asteroids' information (list of list)
    map_width: width of the game field (int)
    map_height: height of the game field (int)

    Notes
    -----
    Create players' data structure and read the config file.

    Version
    -------
    Specifications: Jules Dejaeghere (v.1 26/02/2018)
                    Jules Dejaeghere (v.2 23/03/2018)
    Implementation: Jules Dejaeghere (v.1 07/03/2018)
                    Martin Balfroid (v.2 10/03/2018)
                    Jules Dejaeghere (v.3 23/03/2018)
                    Martin Balfroid (v.4 22/04/2018)
    """

    # Creating data structures
    players = [{
        'ore': 4, 'total_ore': 4, 'portal_life': 100,
        'type': player1[1], 'name': player1[0]},

        {'ore': 4, 'total_ore': 4, 'portal_life': 100,
         'type': player2[1], 'name': player2[0]}]

    asteroids = []
    map_width, map_height = 0, 0

    # Reading config file and filling data structures
    if os.path.isfile(path):

        config = open(path, 'r')
        lines = config.readlines()
        config.close()

        # Delete the '\n' at the end of each line
        for index, line in enumerate(lines):
            line = line.rstrip('\n')

            # Setting map size
            if line == 'size:':
                size = lines[index + 1].rstrip('\n').split()
                map_height = int(size[0])
                map_width = int(size[1])

            elif line == 'portals:':
                # Get the coordinates of each portal
                players[0]['portal'] = tuple([int(x) for x in lines[index + 1].rstrip('\n').split()])
                players[1]['portal'] = tuple([int(x) for x in lines[index + 2].rstrip('\n').split()])

            elif line == 'asteroids:':
                asteroids = [[int(data) for data in lines[i].rstrip('\n').split()] for i in range(index + 1, len(lines))]

        print('Configuration file successfully loaded!')

        print('Welcome to %s and %s, let\'s start the game!' % (players[0]['name'], players[1]['name']))
        print('Game started the %s' % datetime.datetime.now())
        return players, asteroids, map_width, map_height

    else:
        print("%s is not a valid file path" % path)



def cmd(ships, players, info_ships, asteroids, map_width, map_height, turn, AI_data, connection):
    """Ask an input from the user and convert it to the data structure 'actions'.

    Parameters
    ----------
    ships: informations about existing ships (dict)
    players: informations about the players (list)
    info_ships: properties of each type of ships (dict)
    asteroids: informations about the asteroids (list)
    map_width: width of the game field (int)
    map_height: height of the game field (int)
    turn: number of turns (int)
    AI_data: AI's saved data (dict)
    connection: connection to remote player (None if no remote player)

    Returns
    -------
    actions: all the action to do for this turn (list of list)

    Notes
    -----
    Check only syntax not semantic.

    Version
    -------
    Specification: Martin Balfroid (v.1 27-02-2018)
                   Jules Dejaeghere (v.2 02-03-2018)
                   Jules Dejaeghere (v.3 30/03/2018)
                   Martin Balfroid (v.4 20/04/2018)
    Implementation: Jules Dejaeghere (v.1 06/03/2018)
                    Jules Dejaeghere (v.2 30/03/2018)
    """

    tmp_actions = []

    for _ in players:
        tmp_actions.append([[] for _ in range(4)])

    for index, player in enumerate(players):
        message = "It's %s's turn.  What do you want to play? " % player['name']

        if player['type'] == 'AI':
            print(message)
            cmds, AI_data = AI.AI(ships, players, info_ships, asteroids, map_width, map_height, turn, index, AI_data)
            
            if connection != None:
                rp.notify_remote_orders(connection, cmds)
        
        elif player['type'] == 'remote':
            if connection is None:
                print('Error while fetching remote orders, check connection settings')
                cmds = ''
            else:
                cmds = rp.get_remote_orders(connection)
                print(message)
                print(cmds)
                
        elif player['type'] == 'human':
            cmds = input(message)
            if connection != None:
                print(type(cmds))
                print('Will send %s to connection: %s' % (cmds, connection))
                rp.notify_remote_orders(connection, cmds)
        
        else:
            print('Unknown type of player')
            cmds = ''

        cmds = cmds.split()
        # Translating command input of the user into a temporary data structure
        for command in cmds:

            # Handle fire actions
            if ':*' in command:
                tmp = [command.split(':*')[0]]
                try:
                    target = command.split(':*')[1].split('-')
                    for i, element in enumerate(target):
                        target[i] = int(element)
                    tmp += [tuple(target), index]
                except ValueError:
                    tmp += [target, index]
                tmp_actions[index][3] += [tmp]
            # Handle move actions
            elif ':@' in command:
                tmp = [command.split(':@')[0]]
                try:
                    target = command.split(':@')[1].split('-')
                    for i, element in enumerate(target):
                        target[i] = int(element)
                    tmp += [tuple(target), index]
                except ValueError:
                    tmp += [target, index]
                tmp_actions[index][2] += [tmp]
            # Handle lock and release actions
            elif ':lock' in command or ':release' in command:
                tmp = command.split(':')
                tmp.append(index)
                tmp_actions[index][1] += [tmp]
            # Handle buy actions
            elif ':' in command:
                tmp = command.split(':')
                tmp.append(index)
                tmp_actions[index][0] += [tmp]
            else:
                print("Syntax error in the following command '%s'.  This will be ignored." % command)

    # Init an empty actions data structure
    actions = [[], [], [], []]

    # Convert the temporary structure into the actions structure
    for batch in tmp_actions:
        for i in range(len(batch)):
            actions[i] += batch[i]
    return actions


def buy(info_ships, actions, ships, players):
    """Buy a new ship if it's a legal action.
    
    Parameters
    ----------
    info_ships : information about the differents models of ships (dict of dict)
    actions: all the action to do for this turn (list of list)
    ships: structure containing information about ships on the board (dict of dict)
    players: structure that contain the informations of players ( list of dict )

    Returns
    -------
    ships: updated structure containing the ships' informations
    players : update the new 'ore' information of the player
    
    Version
    -------
    Specification : Antoine Janssen (v.1 25/02/2018)
                    Jules Dejaeghere (v.2 04/03/2018)
                    Jules Dejaeghere (v.3 09/03/2018)
                    Antoine Janssen (v.4 10/03/2018)
    Implementation : Antoine Janssen (v.1 11/03/2018)
    """

    buy_actions = actions[0]

    for action in buy_actions:
        # Variable used in this function
        name = action[0]
        ship_type = action[1]
        player = action[2]

        # Add the bought ships into the ships structure
        ships[(name, player)] = {
            'type': ship_type,
            'load': 0,
            'life': info_ships[ship_type]['life'],
            'position': players[player]['portal'],
            'player': player,
            'state': 'unlocked'}

        players[player]['ore'] -= info_ships[ship_type]['cost']

    return ships, players


def lock(actions, ships):
    """Lock or unlock an asteroid or a portal if it's a legal action.

    Parameters
    ----------
    actions : action structure to see if the player locked an asteroids or portal (list of list)
    ships: structure containing ships' informations (dict of dict)

    Returns
    -------
    ships: updated structure containing ships' informations (dict of dict)

    Version
    -------
    specification : Antoine Janssen (v.1 25/02/2018)
    implementation : Antoine Janssen (v.1 11/03/2018)
    """

    for action in actions[1]:
        ships[(action[0], action[2])]['state'] = 'locked' if action[1] == 'lock' else 'unlocked'

    return ships


def move(ships, actions):
    """Move ships according to the actions structure.

    Parameters
    ----------
    ships: structure containing ships' informations (dict of dict)
    actions: structure containing actions' informations (list of list)
    
    Returns
    -------
    ships: updated structure containing ships' informations (dict of dict)

    Version
    -------
    Specifications: Jules Dejaeghere (v.1 26/02/2018)
                    Jules Dejaeghere (v.2 09/03/2018)
                    Jules Dejaeghere (v.3 11/03/2018)
    Implementation: Jules Dejaeghere (v.1 09/03/2018)
                    Jules Dejaeghere (v.2 11/03/2018)
    """

    # For all action update ship position
    for action in actions[2]:
        ships[(action[0], action[2])]['position'] = list(action[1])

    return ships


def fire(actions, ships, players, info_ships):
    """Fire at the target position.

    Parameters
    ----------
    actions: all the  actions for this turn (list of list)
    ships: informations about existing ships (dict)
    players: structure containing players' informations (list of dict)
    info_ships: properties of each type of ships (dict)

    Returns
    -------
    hit: return True if a ship was hit (bool)
    ships: updated informations about existing ships (dict)
    players: structure containing players' informations (list of dict) 

    Notes
    -----
    If a ship is hit and destroyed, it will be deleted from the data structure ships

    Version
    -------
    Specification: Martin Balfroid (v.1 27-02-2018)
                    Jules Dejaeghere (v.2 09/03/2018)
                    Jules Dejaeghere (v.3 11/03/2018)
    Implementation: Jules Dejaeghere (v.1 09/03/2018)
                    Jules Dejaeghere (v.2 11/03/2018)
                    Martin Balfroid (v.3 15/04/2018)
    """

    # Keep only fire actions
    actions = actions[3]

    # Create the portal figure for the hit box
    portal_fig = []
    for y in range(-2, 2 + 1):
        portal_fig += [(y, x) for x in range(-2, 2 + 1) if not (y, x) in [(0, 0)]]

    hit = False
    for action in actions:
        target = tuple(action[1])

        # Check if shoot hit a ship
        for ship in ships:
            ship_hitbox = hitbox(tuple(ships[ship]['position']), info_ships[ships[ship]['type']]['fig'])

            if target in ship_hitbox:
                hit = True
                ships[ship]['life'] -= info_ships[ships[(action[0], action[2])]['type']]['attack']

        # Check if shoot hit a portal 
        for index in range(len(players)):
            portal_hitbox = hitbox(tuple(players[index]['portal']), portal_fig)

            if target in portal_hitbox:
                hit = True
                players[index]['portal_life'] -= info_ships[ships[(action[0], action[2])]['type']]['attack']
                players[index]['portal_life'] = 0 if players[index]['portal_life'] < 0 else players[index]['portal_life']

    # Keep only alive ships
    ships = {ship_name: ship_info for (ship_name, ship_info) in ships.items() if ship_info['life'] > 0}

    return hit, ships, players


def grab_ore(ships, players, asteroids, info_ships):
    """Handle ore mining.

    Parameters
    ----------
    ships: structure containing ships' informations (dict of dict)
    players: structure containing players' informations (list of dict)
    asteroids: structure containing asteroids' informations (list of list)
    info_ships: properties of each type of ships (dict)

    Returns
    -------
    ships: updated structure containing ships' informations (dict of dict)
    players: updated structure containing players' informations (list of dict)
    asteroids: updated structure containing asteroids' informations (list of list)

    Notes
    -----
    Give ore to ships according to their maximum load and asteroids informations.
    Also handle ore transfer from ships to player's inventory.

    Version
    -------
    Specification:  Jules Dejaeghere (v.1 26/02/2018)
                    Jules Dejaeghere (v.2 08/03/2018)
    Implementation: Jules Dejaeghere (v.1 08/03/2018)
                    Jules Dejaeghere (v.2 30/03/2018)
                    Martin Balfroid (v.3 15/04/2018)
    """
    # Handle mining asteroids
    for index, asteroid in enumerate(asteroids):
        ast_pos = tuple(asteroid[0:2])

        # Listing ships fixed on asteroid and loadable
        ships_on_ast = [ship for ship in ships if (ships[ship]['state'] == 'locked'
           and tuple(ships[ship]['position']) == ast_pos
           and ships[ship]['load'] < info_ships[ships[ship]['type']]['max_load'])]

        # Check if enough ore on asteroid to give the maximum to all the ships
        if (len(ships_on_ast) * asteroid[3]) < asteroid[2]:
            mined_ore = 0

            for ship in ships_on_ast:
                free_space = info_ships[ships[ship]['type']]['max_load'] - ships[ship]['load']

                # Check if ship can receive all the ore given by the asteroid
                # If it is the case, give it, else give the maximum it can carry
                grabbed_ore = asteroid[3] if free_space >= asteroid[3] else free_space
                ships[ship]['load'] += grabbed_ore
                mined_ore += grabbed_ore

            # Update amount of ore left on asteroid
            asteroids[index][2] -= mined_ore

        else:
            eligible_ships = ships_on_ast[:]
            ore_on_ast = asteroid[2]

            while len(eligible_ships) > 0 and ore_on_ast > 0:
                for_each = (asteroid[2] / len(eligible_ships)
                            if (asteroid[2] / len(eligible_ships)) < asteroid[3]
                            else asteroid[3])

                for ship_index, ship in enumerate(eligible_ships):
                    free_space = info_ships[ships[ship]['type']]['max_load'] - ships[ship]['load']

                    # Check if ship can receive the defined amount
                    # If it is the case, give it, else give the maximum it can carry
                    receive_max = False
                    if free_space >= for_each:
                        grabbed_ore = for_each
                        receive_max = True
                    else:
                        grabbed_ore = free_space
                    ships[ship]['load'] += grabbed_ore
                    ore_on_ast -= grabbed_ore
                    if receive_max:
                        eligible_ships[ship_index] = None

                # Keep only ships that can carry more ore
                eligible_ships = [ship for ship in eligible_ships if eligible_ships[ship_index] is not None]
                eligible_ships = [ship for ship in eligible_ships if
                                  ships[ship]['load'] < info_ships[ships[ship]['type']]['max_load']]

            # Update amount of ore left on asteroid
            asteroids[index][2] = ore_on_ast

    # Handle delivery to player's portal
    for index in range(len(players)):
        portal_center = players[index]['portal']

        # Listing ship on portal and ready for delivery (locked with more than 0 ore)
        ships_on_portal = [ship for ship in ships if (
            ships[ship]['state'] == 'locked'
            and ships[ship]['player'] == index
            and tuple(ships[ship]['position']) == portal_center
            and ships[ship]['load'] > 0)]

        # Transfering or from ship to portal
        for ship in ships_on_portal:
            players[index]['ore'] += ships[ship]['load']
            players[index]['total_ore'] += ships[ship]['load']
            print("%d ore transfered from %s to portal of %s" % (ships[ship]['load'], ship, players[index]['name']))
            ships[ship]['load'] = 0

    return ships, players, asteroids


def display(ships, players, info_ships, asteroids, map_width, map_height):
    """Print the map with useful information about the state of the game.

    Parameters
    ----------
    ships: informations about existing ships (dict)
    players: informations about the players (list)
    info_ships: properties of each type of ships (dict)
    asteroids: informations about the asteroids (list)
    map_width: width of the game field (int)
    map_height: height of the game field (int)

    Version
    -------
    Specification:  Martin Balfroid (v.1 27-02-2018)
                    Martin Balfroid (v.2 06-03-2018)
                    Martin Balfroid (v.3 08-03-2018)
                    Martin Balfroid (v.4 19-03-2018)
    Implementation: Martin Balfroid (v.1 06-03-2018)
                    Martin Balfroid (v.2 07-03-2018)
                    Martin Balfroid (v.3 08-03-2018)
                    Martin Balfroid (v.4 19-03-2018)
    """

    # (1) Create the game map (without the coordinates)

    # First layer : the void
    # Initiate the game map to be an empty map
    game_map = [['.' for _ in range(map_width)] for _ in range(map_height)]

    # Second layer : portal
    portal_fig = []
    for x in range(-2, 2 + 1):
        portal_fig += [(x, y) for y in range(-2, 2 + 1) if (x, y) != (0, 0)]

    game_info_msg = colored('PLAYERS:\n', attrs=['underline'])
    for ply_id, ply in enumerate(players):
        color = 'blue' if ply_id == 0 else 'red'
        center_pos = ply['portal']

        # Around the portal
        for point in hitbox(center_pos, portal_fig):
            game_map[point[0] - 1][point[1] - 1] = colored('#', color)
        # Portal center
        game_map[center_pos[0] - 1][center_pos[1] - 1] = colored('P', color)

        # Informations about the players
        game_info_msg += ' ' * 4 + colored('%s:\n' % ply['name'], color)
        game_info_msg += ' ' * 8 + colored('%d ore(s) (TOTAL: %d)\n' % (ply['ore'], ply['total_ore']), color)
        game_info_msg += ' ' * 8 + colored('Portal in (%d, %d)\n' % (center_pos[0], center_pos[1]), color)
        game_info_msg += ' ' * 8 + colored('%d/100 HP\n' % ply['portal_life'], color)

    # Third layer : Ships
    game_info_msg += colored('SHIPS:\n', attrs=['underline'])
    for (ship_name, ship) in ships.items():
        ship_type = ship['type']
        color = 'blue' if ship['player'] == 0 else 'red'
        ship_center = ship['position']
        ship_fig = info_ships[ship_type]['fig']
        fig_char = 'X' if ship['state'] == 'locked' else '@'

        # Around the ship
        for point in hitbox(ship_center, ship_fig):
            # All the opponent's ships
            oships = [oship for oship in ships.values() if oship['player'] != ship['player']]
            # The centers of each opponent's ships
            oships_centers = [oship['position'] for oship in oships]
            # The figures of each opponent's ships
            oships_figs = [info_ships[oship['type']]['fig'] for oship in oships]

            # Handle superpositions
            superposition = False
            for i in range(len(oships)):
                if point in hitbox(tuple(oships_centers[i]), oships_figs[i]):
                    superposition = True

            game_map[point[0] - 1][point[1] - 1] = (colored(fig_char, 'magenta')
                                                    if superposition
                                                    else colored(fig_char, color))

        # Ship center
        superposition = False
        for i in range(len(oships)):
            if (ship_center[0], ship_center[1]) in hitbox(tuple(oships_centers[i]), oships_figs[i]):
                superposition = True
        game_map[ship_center[0] - 1][ship_center[1] - 1] = (colored('V', 'magenta')
                                                            if superposition
                                                            else colored('V', color))

        # Informations about the ships
        game_info_msg += ' ' * 4 + colored('%s:\n' % ship_name[0], color)
        game_info_msg += ' ' * 8 + colored('Type: %s\n' % ship_type, color)
        game_info_msg += ' ' * 8 + colored('%d/%d HP\n' % (ship['life'], info_ships[ship_type]['life']), color)

        if ship_type not in ('scout', 'warship'):
            game_info_msg += ' ' * 8 + colored('%d/%d ore(s)\n'
                                               % (ship['load'], info_ships[ship_type]['max_load']), color)

            game_info_msg += ' ' * 8 + colored('State: %s\n'
                                               % ship['state'], color)

        game_info_msg += ' ' * 8 + colored('Position: (%d, %d)\n'
                                           % (ship['position'][0], ship['position'][1]), color)

    # Last Layer : Asteroids
    game_info_msg += colored('ASTEROIDS:\n', attrs=['underline'])

    for asteroid in asteroids:
        # All the locked ships on this asteroid
        locked_ships_on = [ship for ship in ships.values() if (
            ship['state'] == 'locked'
            and ship['position'] == [asteroid[0], asteroid[1]])]

        # No ships locked on this asteroid
        if len(locked_ships_on) == 0:
            game_map[asteroid[0] - 1][asteroid[1] - 1] = 'O'

        # There is ships locked on this asteroid
        else:
            color = 'blue' if locked_ships_on[0]['player'] == 0 else 'red'

            if len(locked_ships_on) > 1:
                # The owner of each ships lock on this asteroid
                owners = [ship['player'] for ship in locked_ships_on]

                # Check if there is ships from different players
                if 0 in owners and 1 in owners:
                    color = 'magenta'

            game_map[asteroid[0] - 1][asteroid[1] - 1] = colored('Ø', color)

        # Informations about the asteroids (hide if empty)
        if asteroid[2] != 0:
            game_info_msg += (' ' * 4 + '(%d, %d) : %d ore(s) left (-%d ore(s) per turn)\n'
                          % (asteroid[0], asteroid[1], asteroid[2], asteroid[3]))

    # (2) Create the display map (with the coordinates)
    # The first 2 lines indicates the abcissa
    display_map = [[' ', ' '] + [str(x // 10) for x in range(1, map_width + 1)],
                   [' ', ' '] + [str(x % 10) for x in range(1, map_width + 1)]]

    # The first 2 columns indicates the ordinates
    ordinates_columns = [[str(y // 10), str(y % 10)] for y in range(1, map_height + 1)]
    # The next lines and columns represent the game_field
    gamefield_columns = [[game_map[y][x] for x in range(map_width)] for y in range(map_height)]
    display_map += [ordinates_columns[y] + gamefield_columns[y] for y in range(map_height)]

    # (3) Display the map
    str_display_map = ''

    for x in range(map_width + 2):
        for y in range(map_height + 2):
            str_display_map += display_map[y][x]
        str_display_map += '\n'

    print(str_display_map)

    # (4) Display informations about the game
    print(game_info_msg)


def end(players, turn_wo_dmg, turn_wo_dmg_max, connection):
    """Show a message at the end of the game, to see who win and who loose.

    Parameters
    ----------
    players: structure containing players' informations (list of dict)
    turn_wo_dmg: number of turn without damage (int)
    turn_wo_dmg_max: the max of turn without damage (int)
    connection: connection to remote player (None if no remote player)

    Version
    -------
    Specification : Antoine Janssen (v.1 25/02/2018)
                    Jules Dejaeghere(v.2 09/03/2018)
                    Martin Balfroid (v.3 30/03/2018)
    Implementation: Martin Balfroid (v.1 16/03/2018)
    """
    ply1 = players[0]
    ply2 = players[1]
    if connection is not None:
        rp.disconnect_from_player(connection)

    # Check the life of the portals to determine a winner.  
    if turn_wo_dmg >= turn_wo_dmg_max or (ply1['portal_life'] <= 0 and ply2['portal_life'] <= 0):
        if ply1['total_ore'] > ply2['total_ore']:
            print('%s win !' % ply1['name'])
        elif ply1['total_ore'] < ply2['total_ore']:
            print('%s win !' % ply2['name'])
        else:
            print('Nobody win !')
    elif ply1['portal_life'] <= 0:
        print('%s win !' % ply2['name'])
    elif ply2['portal_life'] <= 0:
        print('%s win !' % ply1['name'])



def distance(a, b):
    """Compute the Manhattan distance between point a and point b.

    Parameters
    ----------
    a: the coordinates of the point A (2-sized tuple)
    b: the coordinates of the point B (2-sized tuple)

    Return
    ------
    distance: the distance between point a and point b (float)

    Notes
    -----
    a and b must be in the map

    Version
    -------
    Specification: Martin Balfroid (v.1 02/03/2018)
    Implementation: Martin Balfroid (v.1 06/03/2018)
    """

    # 0 is the abcissa and 1 is the ordinate of the point
    return abs(b[0] - a[0]) + abs(b[1] - a[1])


def point_in_map(a, map_width, map_height):
    """Check if the point A is in the map.

    Parameters
    ----------
    a: the coordinates of the point A (2-sized tuple)
    map_width: width of the game field (int)
    map_height: height of the game field (int)

    Return
    ------
    in_map: return True if point A is in the map, False otherwise (bool)

    Version
    -------
    Specification: Martin Balfroid (v.1 02/03/2018)
    Implementation: Martin Balfroid (v.1 06/03/2018)
                    Jules Dejaeghere (v.2 23/03/2018)
    """
    # 0 is the ordinates and 1 is the abcissa
    return (0 < a[0] <= map_height) and (0 < a[1] <= map_width)


def hitbox(center, fig):
    """Return a list containing all the points of the ship.

    Parameters
    ----------
    center: the center of the ship (2-sized tuple)
    fig: the figure of the ship (list of 2-sized tuple)

    Return
    ------
    hitbox: list containing all the points of the ship (list of 2-sized tuple)

    Version
    -------
    Specification: Martin Balfroid (v.1 02/03/2018)
    Implementation: Martin Balfroid (v.1 06/03/2018)
    """

    hitbox = [center]
    for relative_point in fig:
        absolute_point = (relative_point[0] + center[0],
                          relative_point[1] + center[1])

        hitbox.append(absolute_point)

    return hitbox


def ship_in_map(hitbox, map_width, map_height):
    """Check if the ship is in the map.

    Parameters
    ----------
    hitbox: the ship's hitbox (list of 2-sized tuple)
    map_width: width of the game field (int)
    map_height: height of the game field (int)

    Return
    ------
    in_map: return True if point A is in the map, False otherwise (bool)

    Version
    -------
    Specification: Martin Balfroid (v.1 02/03/2018)
    Implementation: Martin Balfroid (v.1 06/03/2018)
    """

    for point in hitbox:
        if not point_in_map(point, map_width, map_height):
            return False

    return True


def point_in_ship(a, hitbox):
    """Check if the point A is in the ship.

    Parameters
    ----------
    a: the coordinates of the point A (2-sized tuple)
    hitbox: the ship's hitbox (list of 2-sized tuple)

    Return
    ------
    hit: return True if point A is in the hitbox, False otherwise (bool)

    Version
    -------
    Specification: Martin Balfroid (v.1 02/03/2018)
    Implementation: Martin Balfroid (v.1 06/03/2018)
    """

    return a in hitbox


# Deprecated
def dummy_AI(ships, player, info_ships, asteroids, map_width, map_height, turn, index):
    """The dummy version of the AI.
    WARNING: deprecated

    Parameters
    ----------
    ships: informations about existing ships (dict)
    player: informations the AI player (dict)
    info_ships: properties of each type of ships (dict)
    asteroids: informations about the asteroids (list)
    map_width: width of the game field (int)
    map_height: height of the game field (int)
    turn: number of turns (int)
    index: index of the AI player in the players structure (int)

    Return
    ------
    AI_actions: commands of the AI (str)

    Version
    -------
    Specifications: Jules Dejaeghere (v.1 02/03/2018)
                    Jules Dejaeghere (v.2 30/03/2018)
                    Jules Dejaeghere (v.3 15/04/2018)
                    Martin Balfroid (v.4 20/04/2018)
    Implementation: Jules Dejaeghere (v.1 30/03/2018)
                    Jules Dejaeghere (v.2 15/04/2018)
    """

    # Creating variables
    budget = player['ore']
    AI_actions = ''

    # Buy ships (as many as possible)
    if budget > 0:
        i = 0
        while budget > 0 and i < 5:
            affordable = [ship for ship in info_ships if info_ships[ship]['cost'] <= budget]
            if len(affordable) > 0:
                ship_type = random.choice(affordable)
                ship_name = str(turn) + '_' + str(random.randint(0, 1000))
                AI_actions += ship_name + ':' + ship_type + ' '
                budget -= info_ships[ship_type]['cost']
            i += 1

    # Lock and unlock ships if needed            
    for ship in [item for item in ships if item[1] == index]:
        for asteroid in asteroids:

            # Check for releasing
            if (ships[ship]['position'] == asteroid[0:2]
                and ships[ship]['state'] == 'locked'
                and ships[ship]['load'] == info_ships[ships[ship]['type']]['max_load']
                and 'excavator' in ships[ship]['type']):

                AI_actions += ship[0] + ':' + 'release '

            # Check for locking    
            elif (ships[ship]['position'] == asteroid[0:2]
                  and ships[ship]['state'] == 'unlocked'
                  and ships[ship]['load'] < info_ships[ships[ship]['type']]['max_load']
                  and 'excavator' in ships[ship]['type']):

                AI_actions += str(ship[0]) + ':' + 'lock '

    # Move or fire (or do nothing)
    for ship in [item for item in ships if item[1] == index]:
        choice = random.choice(['*', '@', None])

        # Generate fire action
        if choice == '*' and 'excavator' not in ships[ship]['type']:
            ship_range = info_ships[ships[ship]['type']]['range']
            ship_position = ships[ship]['position']
            relative_target = [random.randint(-ship_range // 2, ship_range // 2),
                               random.randint(-ship_range // 2, ship_range // 2)]

            target = (ship_position[0] + relative_target[0], ship_position[1] + relative_target[1])

            AI_actions += str(ship[0]) + ':*' + str(target[0]) + '-' + str(target[1]) + ' '

        # Generate move action
        elif choice == '@':
            ship_position = ships[ship]['position']
            relative_target = [random.randint(-1, 1), random.randint(-1, 1)]

            target = (ship_position[0] + relative_target[0], ship_position[1] + relative_target[1])

            AI_actions += str(ship[0]) + ':@' + str(target[0]) + '-' + str(target[1]) + ' '

            # Delete last character of the string if it is a space
    if len(AI_actions) > 0 and AI_actions[-1] == ' ':
        AI_actions = AI_actions[:-1]

    print(AI_actions)
    return AI_actions

 
def legality(action, actions, act_type, ships, info_ships, players, map_width, map_height, display=True):
    """Check if an action is legal.

    Parameters
    ----------
    action: the action being verified (list)
    actions: structure containing actions informations (list of list)
    act_type: the type of the action being verified (str)
    ships: informations about existing ships (dict)
    info_ships: properties of each type of ships (dict)
    players: informations about the players (list)
    map_width: width of the game field (int)
    map_height: height of the game field (int)
    display: True to show messages, False otherwise [default = True] (bool)

    Return
    ------
    legality : return True if the action is legal, False otherwise (bool)

    Notes
    -----
    Check only semantic not syntax.
    Parameter 'act_type' must be in ['buy', 'lock', 'move', 'fire'] if not, function return False

    Version
    -------
    Specification: Antoine Janssen (v.1 : 02/03/2018)
                   Jules Dejaeghere (v.2 02-03-2018)
                   Jules Dejaeghere (v.3 06/03/2018)
                   Jules Dejaeghere (v.4 30/03/2018)
    Implementation: Jules Dejaeghere (v.1 06/03/2018)
                    Jules Dejaeghere (v.2 07/03/2018)
                    Jules Dejaeghere (v.3 11/03/2018)
                    Jules Dejaeghere (v.4 15/03/2018)
                    Jules Dejaeghere (v.5 30/03/2018)
    """

    if act_type == 'buy':
        # Ship type exists?
        if not (action[1] in info_ships):
            print("Cannot buy one %s, unknown type of ship.  In: %s:%s by %s"
                  % (action[1], action[0], action[1], players[action[2]]['name'])) if display else None
            return False

        # Enough money to pay?
        elif not (info_ships[action[1]]['cost'] <= players[action[2]]['ore']):
            print("Need more money to buy one %s  In: %s:%s by %s"
                  % (action[1], action[0], action[1], players[action[2]]['name'])) if display else None
            return False

    elif act_type == 'lock':
        # Ship exists?
        if not (action[0], action[2]) in ships:
            print("Ship %s does not exists.  In: %s:%s by %s"
                  % (action[0], action[0], action[1], players[action[2]]['name'])) if display else None
            return False

        # Does the player own the ship?
        elif not (action[2] == ships[(action[0], action[2])]['player']):
            print("%s does not own %s.  In: %s:%s by %s"
                  % (players[action[0]]['name'], action[0], action[0], action[1],
                     players[action[2]]['name'])) if display else None
            return False

        # Check if ship is lockable
        elif not (info_ships[ships[(action[0], action[2])]['type']]['lockable']):
            print("%s is not lockable.  In: %s:%s by %s"
                  % (action[0], action[0], action[1], players[action[2]]['name'])) if display else None
            return False

        # Ship already in this state?
        elif ((action[1] == 'lock' and ships[(action[0], action[2])]['state'] == 'locked')
              or (action[1] == 'release' and ships[(action[0], action[2])]['state'] == 'unlocked')):
            print("%s is already %s.  In: %s:%s by %s"
                  % (action[0], ships[(action[0], action[2])]['state'],
                     action[0], action[1], players[action[2]]['name'])) if display else None
            return False

    elif act_type == 'move':
        # Check destination format
        if not len(action[1]) == 2:
            print("Invalid destination (length).  In: %s:@%s by %s"
                  % (action[0], action[1], players[action[2]]['name'])) if display else None
            return False

        # Check destination format
        elif not (type(action[1][0]) == type(0) and type(action[1][1]) == type(0)):
            print("Invalid destination (type).  In: %s:@%s by %s"
                  % (action[0], action[1], players[action[2]]['name'])) if display else None
            return False

        # Ship exists?
        elif not (action[0], action[2]) in ships:

            print("Ship %s does not exists.  In: %s:@%s-%s by %s"
                  % (action[0], action[0], action[1][0], action[1][1],
                     players[action[2]]['name'])) if display else None
            return False

        # Does the player own the ship?
        elif not (action[2] == ships[(action[0], action[2])]['player']):
            print("%s belong to %s.  In: %s:@%s-%s by %s"
                  % (action[0], players[ships[(action[0], action[2])]['player']]['name'], action[0],
                     action[1][0], action[1][1], players[action[2]]['name'])) if display else None
            return False

        # Check if ship is not locked.  If locked check if an unlock order has been sent
        elif (ships[(action[0], action[2])]['state'] == 'locked'
              and not (action[0] in [item[0] for item in actions[1] if item[2] == action[2]
            and item[1] == 'release'])):
            print("Cannot move %s because it is locked.  In: %s:@%s-%s by %s"
                  % (action[0], action[0], action[1][0], action[1][1], players[action[2]]['name'])) if display else None
            return False

        # Check if ship is subject to a lock order in this turn
        elif action[0] in [item[0] for item in actions[1] if item[2] == action[2] and item[1] == 'lock']:
            print("%s received a lock order this turn. In: %s:@%s-%s by %s"
                  % (action[0], action[0], action[1][0], action[1][1], players[action[2]]['name'])) if display else None
            return False

        # Check if destination is in map
        elif not (
                ship_in_map(hitbox(tuple(action[1]), info_ships[ships[(action[0], action[2])]['type']]['fig']),
                            map_width,
                            map_height)):
            print("Destination not in map.  In: %s:@%s-%s by %s"
                  % (action[0], action[1][0], action[1][1], players[action[2]]['name'])) if display else None
            return False

        # Move just of 1 position?
        else:
            # Create list of vectors
            vectors = []
            for i in range(-1, 2):
                for j in range(-1, 2):
                    vectors.append((i, j))
            if not (action[1] in hitbox(tuple(ships[(action[0], action[2])]['position']), vectors)):
                print("Destination out of range.  In: %s:@%s-%s by %s"
                      % (action[0], action[1][0], action[1][1], players[action[2]]['name'])) if display else None
                return False

    elif act_type == 'fire':
        # Check target validity
        if not len(action[1]) == 2:
            print("Invalid target (length).  In: %s:@%s by %s"
                  % (action[0], action[1], players[action[2]]['name'])) if display else None
            return False

        # Check target validity
        elif not (isinstance(action[1][0], int)
                  and isinstance(action[1][1], int)):
            print("Invalid target (type).  In: %s:@%s by %s"
                  % (action[0], action[1], players[action[2]]['name'])) if display else None
            return False

        # Ship exists?    
        elif not (action[0], action[2]) in ships:
            print("Ship %s does not exists.  In: %s:*%s-%s by %s"
                  % (action[0], action[0], action[1][0], action[1][1], players[action[2]]['name'])) if display else None
            return False

        # Does the player own the ship?
        elif not (action[2] == ships[(action[0], action[2])]['player']):
            print("%s belong to %s.  In: %s:*%s-%s by %s"
                  % (action[0], players[ships[(action[0], action[2])]['player']]['name'], action[0],
                     action[1][0], action[1][1], players[action[2]]['name'])) if display else None
            return False

        # Check if target in map    
        elif not (point_in_map(tuple(action[1]), map_width, map_height)):
            print("Target not in map.  In: %s:*%s-%s by %s"
                  % (action[0], action[1][0], action[1][1], players[action[2]]['name'])) if display else None
            return False

        # Check if ship already moved this turn
        else:
            # Init a moved variable set to True if considered ship already moved this turn
            moved = False
            move_actions = actions[2]
            for item in move_actions:
                if item[0] == action[0] and item[2] == action[2]:
                    moved = True

            if moved:
                print("%s already moved this turn, a ship cannot move and fire in the same turn.  In: %s:*%s-%s by %s"
                      % (action[0], action[0], action[1][0], action[1][1],
                         players[action[2]]['name'])) if display else None
                return False

        # Fire in range?
        if (distance(ships[(action[0], action[2])]['position'], action[1]) >
                info_ships[ships[(action[0], action[2])]['type']]['range']):
            print("Target out of reach.  In: %s:*%s-%s by %s"
                  % (action[0], action[1][0], action[1][1], players[action[2]]['name'])) if display else None
            return False
    else:
        print("Unknown type of action.  Type must be buy, lock, move or fire.")
        return False

    return True


def clean_actions(actions, ships, info_ships, real_players, map_width, map_height):
    """Delete double fire actions or double move actions for the same ship in the same turn.
    Also delete illegal actions
    
    Parameters
    ----------
    actions: structure containing actions informations (list of list)
    ships: informations about existing ships (dict)
    info_ships: properties of each type of ships (dict)
    real_players: informations about the players (list)
    map_width: width of the game field (int)
    map_height: height of the game field (int)

    Returns
    -------
    clean_actions: cleaned structure containing actions informations (list of list)

    Version
    -------
    Specifications: Jules Dejaeghere (v.1 07/03/2018)
                    Jules Dejaeghere (v.2 11/03/2018)
    Implementation: Jules Dejaeghere (v.1 07/03/2018)
                    Jules Dejaeghere (v.2 11/03/2018)
    """
    # Need to use .copy() method if not Python only copy the reference not the structure
    players = [item.copy() for item in real_players]

    # Defining actions type according to list index
    action_types = ['buy', 'lock', 'move', 'fire']

    # Delete illegal actions
    for index, batch in enumerate(actions):
        for i, action in enumerate(batch):

            if not legality(action, actions, action_types[index], ships, info_ships, players, map_width, map_height):
                # If the action is not legal, it is replaced by None
                batch[i] = None

            elif index == 0:
                players[action[2]]['ore'] -= info_ships[action[1]]['cost']

        # Delete all illegal actions (None items) in the batch
        batch = [item for item in batch if item is not None]
        # Replace the initial batch with the new one
        actions[index] = batch

    # Check for double fire or double move actions
    for i, batch in enumerate(actions):
        commanded_ships = []
        to_delete = []

        # Check if we are dealing with move or fire action
        if i in [2, 3]:

            # Listing all index to delete in batch
            for j, action in enumerate(batch):
                # Check if the ship exists and if the player is the owner of the commanded ship
                if action[0] in ships and action[2] == ships[(action[0], action[2])]['player']:

                    # If ship already commanded this turn, add the action to the queue
                    if action[0] in commanded_ships:
                        to_delete.append(j)
                    # In all cases, add the ship in the list of the commanded ships
                    commanded_ships.append(action[0])

                    # For every action to delete, set the action to None
        for element in to_delete:
            batch[element] = None

        # Redefine the batch with list comprehension, whithout the None elements
        batch = [item for item in batch if item is not None]
        # Replace the initial batch with the new one
        actions[i] = batch

    return actions
