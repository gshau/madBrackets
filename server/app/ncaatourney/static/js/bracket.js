// <script>
  $(document).on('ready', function() {

    var regionList = {{ data['regionList'] | safe }};
    var bracket = {{bracket | safe }};


    var maxTeam = [32, 16, 8, 4, 2, 1];

    var knownBrackets = [2, 4, 8, 16, 32],
      teamsLB1 = {{data['teamNames'][0] | safe}},
      teamsLB2 = {{data['teamNames'][1] | safe}},
      teamsRB1 = {{data['teamNames'][2] | safe}},
      teamsRB2 = {{data['teamNames'][3] | safe}},
      bracketCount = 0;
    var seeds = {{  data['seeds'] }}
    var opts = 32; //parseInt(prompt('Bracket size (number of teams):',16));
    getBracket(opts, "LB", teamsLB1.concat(teamsLB2), seeds, bracket, false);
    getBracket(opts, "RB", teamsRB1.concat(teamsRB2), seeds, bracket, true);
    // getBracket(opts);
    /*
     * Build our bracket "model"
     */
    function getBracket(base, bracketGroup, teams, seeds, bracket, reverse) {

      var closest = _.find(knownBrackets, function(k) {
          return k >= base;
        }),
        byes = closest - base;

      if (byes > 0) base = closest;

      var brackets = [],
        round = 1,
        baseT = base / 2,
        baseC = base / 2,
        teamMark = 0,
        nextInc = base / 2;

      for (i = 1; i <= (base - 1); i++) {
        var baseR = i / baseT,
          isBye = false;

        if (byes > 0 && (i % 2 != 0 || byes >= (baseT - i))) {
          isBye = true;
          byes--;
        }

        var last = _.map(_.filter(brackets, function(b) {
          return b.nextGame == i;
        }), function(b) {
          return {
            game: b.bracketNo,
            teams: b.teamnames
          };
        });

        brackets.push({
          lastGames: round == 1 ? null : [last[0].game, last[1].game],
          nextGame: nextInc + i > base - 1 ? null : nextInc + i,
          teamnames: round == 1 ? [seeds[teamMark % 16] + '. ' + teams[teamMark], seeds[(teamMark + 1) % 16] + '. ' + teams[teamMark + 1]] : [last[0].teams[_.random(1)], last[1].teams[_.random(1)]],
          bracketNo: i,
          roundNo: round,
          bye: isBye
        });
        teamMark += 2;
        if (i % 2 != 0) nextInc--;
        while (baseR >= 1) {
          round++;
          baseC /= 2;
          baseT = baseT + baseC;
          baseR = i / baseT;
        }
      }
      if (reverse) {
        renderBracketsReverse(brackets, bracketGroup);
      } else {
        renderBrackets(brackets, bracketGroup, bracket);
      }
    }

    /*
     * Inject our brackets
     */
    function renderBrackets(struct, bracketGroup, bracket) {
    var roundNumber = _.uniq(_.map(struct, function(s) {
        return s.roundNo;
      })).length;
      // var roundNum
      var group = $('<div class="group' + (roundNumber + 1) + '" id="b' + bracketCount + '"></div>'),
        grouped = _.groupBy(struct, function(s) {
          return s.roundNo;
        });

      for (iround = 1; iround <= roundNumber; iround++) {
        var round = $('<div class="r' + iround + '"></div>');
        var teamsInThisRound=bracket[iround];
        console.log(teamsInThisRound);
        for (iteam=1; iteam <= maxTeam[iround]; iteam++){
          round.append('<div><div class="bracketbox"><span class="teama">' + teamsInThisRound[2*iteam-2] + '</span><span class="teamb">' + teamsInThisRound[2*iteam-1] + '</span></div></div>');
        }

        group.append(round);
      }
      group.append('<div class="r' + (roundNumber + 1) + 'L"><div class="final"><div class="bracketbox"><span class="teamc">' + bracket[roundNumber+1][0] + '</span></div></div></div>');
      $('#' + bracketGroup).append(group);

      bracketCount++;
    }


    function renderBracketsReverse(struct, bracketGroup) {
      var roundNumber = _.uniq(_.map(struct, function(s) {
        return s.roundNo;
      })).length;
      // var roundNum
      var group = $('<div class="group' + (roundNumber + 1) + '" id="b' + bracketCount + '"></div>'),
        grouped = _.groupBy(struct, function(s) {
          return s.roundNo;
        });
      group.append('<div class="r' + (roundNumber + 1) + 'R"><div class="final"><div class="bracketbox"><span class="teamc">' + bracket[roundNumber+1][1] + '</span></div></div></div>');


      for (iround = roundNumber; iround > 0; iround--) {
        var round = $('<div class="r' + iround + '"></div>');
        var teamsInThisRound=bracket[iround];
        console.log(teamsInThisRound);
        for (iteam=maxTeam[iround]+1; iteam <= 2*maxTeam[iround]; iteam++){
          round.append('<div><div class="bracketboxrev"><span class="teama">' + teamsInThisRound[2*iteam-2] + '</span><span class="teamb">' + teamsInThisRound[2*iteam-1] + '</span></div></div>');
        }

        group.append(round);
      }
      $('#' + bracketGroup).append(group);

      bracketCount++;
    }


  });
// </script>
