(function() {
  var $, AbstractRunFeedingStrategy, AssertionError, Contest, DataLoadError, FIFORunFeedingStrategy, IllegalArgumentError, M, NotImplementedError, Problem, ProblemSummary, Run, RunFeeder, Team, TeamProblemSeparatedQueuedRunFeedingStrategy, TeamProblemStatus, TeamStatus, assert, assertNotNull, deepClone, getObjectClassName, isNaN, shallowClone, stableSort,
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  $ = this.$ || require('jquery');

  if (typeof window === 'undefined') {
    $.extend = require('extend');
  }

  AssertionError = (function(_super) {
    __extends(AssertionError, _super);

    function AssertionError(message, cause) {
      this.message = message;
      this.cause = cause;
      Error.captureStackTrace(this, this);
    }

    return AssertionError;

  })(Error);

  IllegalArgumentError = (function(_super) {
    __extends(IllegalArgumentError, _super);

    function IllegalArgumentError(message, cause) {
      this.message = message;
      this.cause = cause;
      Error.captureStackTrace(this, this);
    }

    return IllegalArgumentError;

  })(Error);

  NotImplementedError = (function(_super) {
    __extends(NotImplementedError, _super);

    function NotImplementedError(message, cause) {
      this.message = message;
      this.cause = cause;
      Error.captureStackTrace(this, this);
    }

    return NotImplementedError;

  })(Error);

  DataLoadError = (function(_super) {
    __extends(DataLoadError, _super);

    function DataLoadError(message, cause) {
      this.message = message;
      this.cause = cause;
      Error.captureStackTrace(this, this);
    }

    return DataLoadError;

  })(Error);

  assert = function(expr, message) {
    if (message == null) {
      message = "Assertion Failed";
    }
    if (!expr) {
      throw new AssertionError(message);
    }
  };

  assertNotNull = function(expr, message) {
    if (message == null) {
      message = "Missing Argument";
    }
    if (!expr) {
      throw new IllegalArgumentError(message);
    }
    return expr;
  };

  getObjectClassName = function(obj) {
    if (obj === null) {
      return null;
    }
    if ((typeof obj) !== "object") {
      return null;
    }
    return /(\w+)\(/.exec(obj.constructor.toString())[1];
  };

  deepClone = function(obj) {
    return $.extend(true, {}, {
      ref: obj
    }).ref;
  };

  shallowClone = function(obj) {
    return $.extend({}, {
      ref: obj
    }).ref;
  };

  isNaN = function(x) {
    return x !== x;
  };

  stableSort = function(arr, comparator) {
    var idx, item;
    for (idx in arr) {
      item = arr[idx];
      item.__stable__idx__ = idx;
    }
    arr.sort(function(x, y) {
      var v;
      v = comparator(x, y);
      if (v === 0) {
        return x.__stable__idx__ - y.__stable__idx__;
      } else {
        return v;
      }
    });
    for (item in arr) {
      delete item.__stable__idx__;
    }
    return arr;
  };

  Problem = (function() {
    function Problem(contest, id, name, title, color) {
      this.contest = contest;
      this.id = id;
      this.name = name;
      this.title = title;
      this.color = color;
      if (!this.name) {
        this.name = this.title.charAt(0);
      }
    }

    Problem.prototype.getContest = function() {
      return this.contest;
    };

    Problem.prototype.getId = function() {
      return this.id;
    };

    Problem.prototype.getName = function() {
      return this.name;
    };

    Problem.prototype.getTitle = function() {
      return this.title;
    };

    Problem.prototype.getColor = function() {
      return this.color;
    };

    Problem.prototype.toString = function() {
      var s;
      s = "Problem " + this.name;
      if (this.title && this.title !== this.name) {
        s += " : " + this.title;
      }
      return s;
    };

    return Problem;

  })();

  Team = (function() {
    function Team(contest, id, name, group) {
      var ex, regx, _ref;
      this.contest = contest;
      this.id = id;
      this.name = name;
      this.group = group != null ? group : null;
      if (!(group != null)) {
        regx = /^([^(]+)\(([^)]*)\)$/.exec(this.name);
        try {
          if (regx) {
            _ref = [regx[1].trim(), regx[2].trim()], this.name = _ref[0], this.group = _ref[1];
          }
        } catch (_error) {
          ex = _error;
          this.group = null;
        }
      }
    }

    Team.prototype.getContest = function() {
      return this.contest;
    };

    Team.prototype.getId = function() {
      return this.id;
    };

    Team.prototype.getName = function() {
      return this.name;
    };

    Team.prototype.getGroup = function(nullAsEmpty) {
      if (nullAsEmpty == null) {
        nullAsEmpty = false;
      }
      if (nullAsEmpty && this.group === null) {
        return "";
      }
      return this.group;
    };

    return Team;

  })();

  TeamStatus = (function() {
    function TeamStatus(contest, team) {
      this.contest = contest;
      this.team = team;
      this.solved = 0;
      this.penalty = 0;
      this.lastSolvedTime = 0;
      this.rank = 1;
      this.problemStatuses = {};
      this.cache = {};
    }

    TeamStatus.prototype.getContest = function() {
      return this.contest;
    };

    TeamStatus.prototype.getTeam = function() {
      return this.team;
    };

    TeamStatus.prototype.getRank = function() {
      return this.rank;
    };

    TeamStatus.prototype.getProblemStatus = function(problem) {
      var problemStatus;
      problem = this.contest.getProblem(problem);
      problemStatus = this.problemStatuses[problem.getId()];
      if (problemStatus == null) {
        problemStatus = this.problemStatuses[problem.getId()] = new TeamProblemStatus(this.contest, this, problem);
      }
      return problemStatus;
    };

    TeamStatus.prototype.getTotalAttempts = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.totalAttempts) != null ? _ref : this.cache.totalAttempts = (function() {
        var pid, ps, s, _ref1;
        s = 0;
        _ref1 = _this.problemStatus;
        for (pid in _ref1) {
          ps = _ref1[pid];
          s += ps.getAttempts();
        }
        return s;
      })();
    };

    TeamStatus.prototype.getTotalSolved = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.totalSolved) != null ? _ref : this.cache.totalSolved = (function() {
        var pid, ps, s, _ref1;
        s = 0;
        _ref1 = _this.problemStatuses;
        for (pid in _ref1) {
          ps = _ref1[pid];
          if (ps.isAccepted()) {
            s++;
          }
        }
        return s;
      })();
    };

    TeamStatus.prototype.getPenalty = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.penalty) != null ? _ref : this.cache.penalty = (function() {
        var pid, ps, s, _ref1;
        s = 0;
        _ref1 = _this.problemStatuses;
        for (pid in _ref1) {
          ps = _ref1[pid];
          s += ps.getContributingPenalty();
        }
        return s;
      })();
    };

    TeamStatus.prototype.getLastSolvedTime = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.lastSolvedTime) != null ? _ref : this.cache.lastSolvedTime = (function() {
        var pid, ps, s, t, _ref1;
        s = 0;
        _ref1 = _this.problemStatuses;
        for (pid in _ref1) {
          ps = _ref1[pid];
          t = ps.getSolvedTime();
          if ((t != null) && t > s) {
            s = t;
          }
        }
        return s;
      })();
    };

    TeamStatus.prototype.hasSolved = function(problem) {
      problem = this.contest.getProblem(problem);
      throw new NotImplementedError;
    };

    TeamStatus.prototype.update = function(run) {
      var ps;
      assert(run.getTeam() === this.getTeam(), 'invalid run update');
      ps = this.getProblemStatus(run.getProblem());
      ps.update(run);
      return this.cache = {};
    };

    return TeamStatus;

  })();

  TeamProblemStatus = (function() {
    function TeamProblemStatus(contest, teamStatus, problem) {
      this.contest = contest;
      this.teamStatus = teamStatus;
      this.problem = problem;
      this.runs = [];
      this.netruns = null;
      this.cache = {};
    }

    TeamProblemStatus.prototype.getAllRuns = function() {
      return this.runs;
    };

    TeamProblemStatus.prototype.getContest = function() {
      return this.contest;
    };

    TeamProblemStatus.prototype.getTeamStatus = function() {
      return this.teamStatus;
    };

    TeamProblemStatus.prototype.getProblem = function() {
      return this.problem;
    };

    TeamProblemStatus.prototype.isAttempted = function() {
      return this.runs.length > 0;
    };

    TeamProblemStatus.prototype.getNetRuns = function() {
      var _ref,
        _this = this;
      return (_ref = this.netruns) != null ? _ref : this.netruns = (function() {
        var netr, run, _i, _len, _ref1;
        netr = [];
        _ref1 = _this.runs;
        for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
          run = _ref1[_i];
          netr.push(run);
          if (run.isJudgedYes()) {
            break;
          }
        }
        return netr;
      })();
    };

    TeamProblemStatus.prototype.getNetLastRun = function() {
      var netr;
      netr = this.getNetRuns();
      if (netr.length === 0) {
        return null;
      }
      return netr[netr.length - 1];
    };

    TeamProblemStatus.prototype.getAttempts = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.attempts) != null ? _ref : this.cache.attempts = (function() {
        return _this.getNetRuns().length;
      })();
    };

    TeamProblemStatus.prototype.getNotAcceptedAttempts = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.notacceptedAttempts) != null ? _ref : this.cache.notacceptedAttempts = (function() {
        var attempts;
        attempts = _this.getNetRuns().length;
        if (_this.isAccepted()) {
          attempts -= 1;
        }
        return attempts;
      })();
    };

    TeamProblemStatus.prototype.getFailedAttempts = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.failedAttempts) != null ? _ref : this.cache.failedAttempts = (function() {
        var attempts, run, _i, _len, _ref1;
        attempts = 0;
        _ref1 = _this.getNetRuns();
        for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
          run = _ref1[_i];
          if (run.isFailed()) {
            attempts += 1;
          }
        }
        return attempts;
      })();
    };

    TeamProblemStatus.prototype.isAccepted = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.accepted) != null ? _ref : this.cache.accepted = (function() {
        var _ref1, _ref2;
        return (_ref1 = (_ref2 = _this.getNetLastRun()) != null ? _ref2.isJudgedYes() : void 0) != null ? _ref1 : false;
      })();
    };

    TeamProblemStatus.prototype.isFailed = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.failed) != null ? _ref : this.cache.failed = (function() {
        var netr, _ref1, _ref2;
        netr = _this.getNetRuns();
        return (_ref1 = (_ref2 = _this.getNetLastRun()) != null ? _ref2.isFailed() : void 0) != null ? _ref1 : false;
      })();
    };

    TeamProblemStatus.prototype.isPending = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.pending) != null ? _ref : this.cache.pending = (function() {
        var netr, _ref1, _ref2;
        netr = _this.getNetRuns();
        return (_ref1 = (_ref2 = _this.getNetLastRun()) != null ? _ref2.isPending() : void 0) != null ? _ref1 : false;
      })();
    };

    TeamProblemStatus.prototype.getContributingPenalty = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.penalty) != null ? _ref : this.cache.penalty = (function() {
        if (_this.isAccepted()) {
          return (_this.getFailedAttempts()) * 20 + _this.getSolvedTime();
        } else {
          return 0;
        }
      })();
    };

    TeamProblemStatus.prototype.getPenaltyMemoString = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.penaltyMemo) != null ? _ref : this.cache.penaltyMemo = (function() {
        if (_this.isAccepted()) {
          if (_this.getFailedAttempts() === 0) {
            return "" + (_this.getSolvedTime());
          } else {
            return "" + (_this.getSolvedTime()) + " + 20 * " + (_this.getFailedAttempts()) + " = " + (_this.getContributingPenalty());
          }
        } else {
          return '';
        }
      })();
    };

    TeamProblemStatus.prototype.getSolvedTime = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.solvedTime) != null ? _ref : this.cache.solvedTime = (function() {
        var run;
        run = _this.getNetLastRun();
        if ((run != null) && run.isJudgedYes()) {
          return run.getTime();
        } else {
          return null;
        }
      })();
    };

    TeamProblemStatus.prototype.getSolvedRun = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.solvedRun) != null ? _ref : this.cache.solvedRun = (function() {
        var run;
        run = _this.getNetLastRun();
        if ((run != null) && run.isJudgedYes()) {
          return run;
        } else {
          return null;
        }
      })();
    };

    TeamProblemStatus.prototype.update = function(run) {
      var found, idx, oldrun, _ref;
      assert(run.getProblem() === this.getProblem());
      assert(run.getContest() === this.getContest());
      found = false;
      _ref = this.runs;
      for (idx in _ref) {
        oldrun = _ref[idx];
        if (oldrun.getId() === run.getId()) {
          this.runs[idx] = run;
          found = true;
          break;
        }
      }
      if (!found) {
        this.runs.push(run);
      }
      this.runs.sort(function(r1, r2) {
        return r1.getId() - r2.getId();
      });
      this.netruns = null;
      return this.cache = {};
    };

    return TeamProblemStatus;

  })();

  ProblemSummary = (function() {
    function ProblemSummary(contest, problem) {
      this.contest = contest;
      this.problem = problem;
      this.runs = [];
      this.cache = {};
    }

    ProblemSummary.prototype.getContest = function() {
      return this.contest;
    };

    ProblemSummary.prototype.getProblem = function() {
      return this.problem;
    };

    ProblemSummary.prototype.update = function(run) {
      assert(run.getProblem() === this.getProblem(), 'invalid run update');
      this.runs.push(run);
      return this.cache = {};
    };

    ProblemSummary.prototype.getAttempts = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.attempts) != null ? _ref : this.cache.attempts = (function() {
        return _this.runs.length;
      })();
    };

    ProblemSummary.prototype.getAccepted = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.accepted) != null ? _ref : this.cache.accepted = (function() {
        var r, rid, run, _ref1;
        r = 0;
        _ref1 = _this.runs;
        for (rid in _ref1) {
          run = _ref1[rid];
          if (run.isAccepted()) {
            r += 1;
          }
        }
        return r;
      })();
    };

    ProblemSummary.prototype.getFailed = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.failed) != null ? _ref : this.cache.failed = (function() {
        var r, rid, run, _ref1;
        r = 0;
        _ref1 = _this.runs;
        for (rid in _ref1) {
          run = _ref1[rid];
          if (run.isFailed()) {
            r += 1;
          }
        }
        return r;
      })();
    };

    ProblemSummary.prototype.getPending = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.pending) != null ? _ref : this.cache.pending = (function() {
        var r, rid, run, _ref1;
        r = 0;
        _ref1 = _this.runs;
        for (rid in _ref1) {
          run = _ref1[rid];
          if (run.isPending()) {
            r += 1;
          }
        }
        return r;
      })();
    };

    ProblemSummary.prototype.getFirstSolvedTime = function() {
      var _ref,
        _this = this;
      return (_ref = this.cache.firstSolvedTime) != null ? _ref : this.cache.firstSolvedTime = (function() {
        var first_time, rid, run, _ref1;
        first_time = 9999999;
        _ref1 = _this.runs;
        for (rid in _ref1) {
          run = _ref1[rid];
          if (run.isAccepted()) {
            first_time = Math.min(first_time, run.getTime());
          }
        }
        return first_time;
      })();
    };

    ProblemSummary.prototype.isFirstSolved = function(problemStatus) {
      if (!(problemStatus instanceof TeamProblemStatus)) {
        throw new Error('#isFirstSolved : should be TeamProblemStatus');
      }
      return problemStatus.getSolvedTime() === this.getFirstSolvedTime();
    };

    return ProblemSummary;

  })();

  Run = (function() {
    function Run(contest, id, problem, team, time, result) {
      this.contest = contest;
      this.id = id;
      this.problem = problem;
      this.team = team;
      this.time = time;
      this.result = result;
      if (this.contest != null) {
        assert(this.contest === this.problem.getContest());
      }
      if (this.contest != null) {
        assert(this.contest === this.team.getContest());
      }
    }

    Run.prototype.clone = function() {
      return new Run(this.contest, this.id, this.problem, this.team, this.time, this.result);
    };

    Run.prototype.getContest = function() {
      return this.contest;
    };

    Run.prototype.getId = function() {
      return this.id;
    };

    Run.prototype.getProblem = function() {
      return this.problem;
    };

    Run.prototype.getTeam = function() {
      return this.team;
    };

    Run.prototype.getTime = function() {
      return this.time;
    };

    Run.prototype.getStatus = function() {
      return this.status;
    };

    Run.prototype.getResult = function() {
      return this.result;
    };

    Run.prototype.isJudgedYes = function() {
      return this.result.substr(0, 3) === "Yes";
    };

    Run.prototype.isAccepted = function() {
      return this.isJudgedYes();
    };

    Run.prototype.isPending = function() {
      return this.result === "" || this.result.substr(0, 7) === "Pending";
    };

    Run.prototype.isFailed = function() {
      return this.result !== "" && !this.isJudgedYes();
    };

    Run.prototype.setStatus = function(newStatus) {
      var changed;
      changed = this.status === newStatus;
      return this.status = newStatus;
    };

    return Run;

  })();

  Contest = (function() {
    function Contest(contestTitle, systemName, systemVersion, problems, teams) {
      var p, pid, t, tid, _i, _j, _len, _len1;
      this.contestTitle = contestTitle;
      this.systemName = systemName;
      this.systemVersion = systemVersion;
      if (problems == null) {
        problems = [];
      }
      if (teams == null) {
        teams = [];
      }
      if (typeof this.contestTitle !== 'string') {
        throw Error("contestTitle must be a string");
      }
      if (typeof this.systemName !== 'string') {
        throw Error("systemName must be a string");
      }
      if (typeof this.systemVersion !== 'string') {
        throw Error("systemVersion must be a string");
      }
      this.problems = [];
      for (_i = 0, _len = problems.length; _i < _len; _i++) {
        p = problems[_i];
        pid = parseInt(p.id);
        if (typeof pid === 'undefined') {
          continue;
        }
        this.problems.push(new Problem(this, pid, p.name, p.title, p.color));
      }
      this.teams = [];
      for (_j = 0, _len1 = teams.length; _j < _len1; _j++) {
        t = teams[_j];
        tid = parseInt(t.id);
        this.teams[tid] = new Team(this, tid, t.name, t.group);
      }
    }

    Contest.createFromJson = function(contest) {
      var contestTitle, problems, systemName, systemVersion, teams, theContest;
      contestTitle = contest['title'] || 'ACM-ICPC Contest';
      systemName = contest['systemName'] || '';
      systemVersion = contest['systemVersion'] || '';
      problems = assertNotNull(contest['problems']);
      teams = assertNotNull(contest['teams']);
      theContest = new Contest(contestTitle, systemName, systemVersion, problems, teams);
      theContest.initialize();
      return theContest;
    };

    Contest.prototype.initialize = function() {
      var problem, team, tid, _i, _len, _ref, _ref1;
      this.teamStatuses = [];
      _ref = this.teams;
      for (tid in _ref) {
        team = _ref[tid];
        this.teamStatuses[team.getId()] = new TeamStatus(this, team);
      }
      this.rankedTeamStatuses = null;
      this.problemSummarys = [];
      _ref1 = this.problems;
      for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
        problem = _ref1[_i];
        this.problemSummarys[problem.getId()] = new ProblemSummary(this, problem);
      }
      this.runsIndexed = {};
      this.underRunTransaction = false;
      return this;
    };

    Contest.prototype.getContestTitle = function() {
      return this.contestTitle;
    };

    Contest.prototype.getSystemName = function() {
      return this.systemName;
    };

    Contest.prototype.getSystemVersion = function() {
      return this.systemVersion;
    };

    Contest.prototype.getProblems = function() {
      return this.problems;
    };

    Contest.prototype.getTeams = function() {
      return this.teams;
    };

    Contest.prototype.getProblem = function(p) {
      var pid, prob, _i, _len, _ref, _ref1;
      if (p instanceof Problem) {
        return p;
      }
      if ((_ref = typeof p) === "number" || _ref === "string") {
        pid = parseInt(p);
        _ref1 = this.problems;
        for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
          prob = _ref1[_i];
          if (prob.id === pid) {
            return prob;
          }
        }
      }
      throw new Error('#getProblem : illegal argument `p`');
    };

    Contest.prototype.getTeam = function(t) {
      var _ref, _ref1;
      if (t instanceof Team) {
        return t;
      }
      if ((_ref = typeof t) === "number" || _ref === "string") {
        t = parseInt(t);
        if (!isNaN(t)) {
          return this.teams[t];
        }
      } else if ((_ref1 = typeof t.id) === "number" || _ref1 === "string") {
        t = parseInt(t.id);
        if (!isNaN(t)) {
          return this.teams[t];
        }
      }
      throw new Error('#getTeam : illegal argument `t`');
    };

    Contest.prototype.getTeamStatus = function(team) {
      team = this.getTeam(team);
      if (!(team instanceof Team)) {
        throw new Error('#getTeamStatus : illegal argument `team`');
      }
      return this.teamStatuses[team.getId()];
    };

    Contest.prototype.getRankedTeamStatusList = function() {
      this.updateTeamStatusesAndRanks();
      return this.rankedTeamStatuses;
    };

    Contest.prototype.getProblemSummary = function(problem) {
      problem = this.getProblem(problem);
      if (!(problem instanceof Problem)) {
        throw new Error('#getProblemSummary : illegal argument `problem`');
      }
      return this.problemSummarys[problem.getId()];
    };

    Contest.prototype.getRuns = function() {
      return this.runsIndexed;
    };

    Contest.prototype.updateTeamStatusesAndRanks = function() {
      var prevTeamStatus, r, rts, teamComparator, teamStatus, tid, ts;
      rts = (function() {
        var _ref, _results;
        _ref = shallowClone(this.teamStatuses);
        _results = [];
        for (tid in _ref) {
          ts = _ref[tid];
          _results.push(ts);
        }
        return _results;
      }).call(this);
      teamComparator = function(t1, t2) {
        if (t1.getTotalSolved() !== t2.getTotalSolved()) {
          return t2.getTotalSolved() - t1.getTotalSolved();
        }
        if (t1.getPenalty() !== t2.getPenalty()) {
          return t1.getPenalty() - t2.getPenalty();
        }
        if (t1.getLastSolvedTime() !== t2.getLastSolvedTime()) {
          return t1.getLastSolvedTime() - t2.getLastSolvedTime();
        }
        return 0;
      };
      stableSort(rts, teamComparator);
      for (r in rts) {
        teamStatus = rts[r];
        teamStatus.rank = parseInt(r) + 1;
      }
      for (r in rts) {
        teamStatus = rts[r];
        if ((r = parseInt(r)) > 0) {
          prevTeamStatus = rts[r - 1];
          if (teamComparator(prevTeamStatus, teamStatus) === 0) {
            teamStatus.rank = prevTeamStatus.rank;
          }
        }
      }
      this.rankedTeamStatuses = rts;
      return rts;
    };

    Contest.prototype.reflectRun = function(run) {
      var problem, problemSummary, rid, team, teamStatus;
      assert(run instanceof Run, 'run is not an instance of Run');
      assert(run.getContest() === this, 'run is out of the contest context');
      rid = run.getId();
      team = run.getTeam();
      problem = run.getProblem();
      this.runsIndexed[rid] = run;
      teamStatus = this.teamStatuses[team.getId()];
      teamStatus.update(run);
      problemSummary = this.problemSummarys[problem.getId()];
      problemSummary.update(run);
      if (!this.underRunTransaction) {
        return this.updateTeamStatusesAndRanks();
      }
    };

    Contest.prototype.beginRunTransaction = function() {
      if (this.underRunTransaction) {
        throw new Error('already in a transaction');
      } else {
        return this.underRunTransaction = true;
      }
    };

    Contest.prototype.commitRunTransaction = function() {
      if (!this.underRunTransaction) {
        throw new Error('not in a transaction');
      } else {
        this.underRunTransaction = false;
        return this.updateTeamStatusesAndRanks();
      }
    };

    return Contest;

  })();

  RunFeeder = (function() {
    function RunFeeder(contest, strategy) {
      this.contest = contest;
      this.strategy = strategy;
      if (!((this.contest != null) && this.contest instanceof Contest)) {
        throw new Error("contest is undefined or null");
      }
      if (this.strategy === void 0) {
        this.strategy = new FIFORunFeedingStrategy();
      }
      this.strategy.setContest(this.contest);
      this.runCount = 0;
      this.contestTime = 0;
      this.lastTimeStamp = 0;
      this.noMoreUpdate = false;
    }

    RunFeeder.prototype.setStrategy = function(strategy) {
      this.strategy = strategy;
      return this.strategy.setContest(this.contest);
    };

    RunFeeder.prototype.getRunCount = function() {
      return this.runCount;
    };

    RunFeeder.prototype.getContestTime = function() {
      return this.contestTime;
    };

    RunFeeder.prototype.getLastTimeStamp = function() {
      return this.lastTimeStamp;
    };

    RunFeeder.prototype.isNoMoreUpdate = function() {
      return this.noMoreUpdate;
    };

    RunFeeder.prototype.parseRunData = function(data, filter) {
      var contestTime, lastTimeStamp, noMoreUpdate, pid, r, rid, run, runs, tid, timestamp, _i, _len, _ref, _ref1, _ref2, _ref3;
      assertNotNull(data['runs']);
      runs = [];
      _ref = data['runs'];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        r = _ref[_i];
        rid = parseInt(r.id);
        pid = parseInt(r.problem);
        if (isNaN(pid)) {
          pid = parseInt((_ref1 = r.problem) != null ? _ref1.id : void 0);
        }
        tid = parseInt(r.team);
        if (isNaN(tid)) {
          tid = parseInt((_ref2 = r.team) != null ? _ref2.id : void 0);
        }
        run = new Run(this.contest, rid, this.contest.getProblem(pid), this.contest.getTeam(tid), parseInt(r.submissionTime), r.result);
        if (run === null) {
          continue;
        }
        if ((filter != null) && !filter(run)) {
          continue;
        }
        runs.push(run);
      }
      noMoreUpdate = contestTime = lastTimeStamp = null;
      if (data['time']) {
        noMoreUpdate = (_ref3 = data['time'].noMoreUpdate) != null ? _ref3 : {
          "true": false
        };
        contestTime = parseInt(data['time'].contestTime);
        timestamp = parseInt(data['time'].timestamp);
      }
      if (timestamp >= 0) {
        lastTimeStamp = timestamp;
      }
      return [runs, noMoreUpdate, contestTime, lastTimeStamp];
    };

    RunFeeder.prototype.fetchRunsFromJson = function(data, filter) {
      var contestTime, lastTimeStamp, noMoreUpdate, runs, _ref;
      _ref = this.parseRunData(data, filter), runs = _ref[0], noMoreUpdate = _ref[1], contestTime = _ref[2], lastTimeStamp = _ref[3];
      if (noMoreUpdate !== null) {
        this.noMoreUpdate = noMoreUpdate;
      }
      if (contestTime !== null) {
        this.contestTime = contestTime;
      }
      if (lastTimeStamp !== null) {
        this.lastTimeStamp = lastTimeStamp;
      }
      return this.fetchRunsFromArray(runs);
    };

    RunFeeder.prototype.diffAndFeedRuns = function(data, filter) {
      var contestTime, lastTimeStamp, noMoreUpdate, run, runs, _ref;
      _ref = this.parseRunData(data, filter), runs = _ref[0], noMoreUpdate = _ref[1], contestTime = _ref[2], lastTimeStamp = _ref[3];
      if (noMoreUpdate !== null) {
        this.noMoreUpdate = noMoreUpdate;
      }
      if (contestTime !== null) {
        this.contestTime = contestTime;
      }
      if (lastTimeStamp !== null) {
        this.lastTimeStamp = lastTimeStamp;
      }
      runs = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = runs.length; _i < _len; _i++) {
          run = runs[_i];
          if (this._isReflectable(run)) {
            _results.push(run);
          }
        }
        return _results;
      }).call(this);
      return this.fetchRunsFromArray(runs);
    };

    RunFeeder.prototype.fetchRunsFromArray = function(runs) {
      var fetched_runs, run, _i, _len;
      fetched_runs = 0;
      for (_i = 0, _len = runs.length; _i < _len; _i++) {
        run = runs[_i];
        this.strategy.pushRun(run);
        this.runCount += 1;
        fetched_runs += 1;
      }
      return fetched_runs;
    };

    RunFeeder.prototype._isReflectable = function(run) {
      var oldRun;
      assert(run instanceof Run, 'run is not an instance of Run');
      assert(run.getContest() === this.contest, 'run is out of the contest context');
      oldRun = null;
      this.runDoEach(function(qrun) {
        if (qrun.getId() === run.getId()) {
          return oldRun = qrun;
        }
      });
      if (!oldRun) {
        oldRun = this.contest.runsIndexed[run.getId()];
      }
      if (!oldRun) {
        return true;
      }
      if (oldRun.isAccepted()) {
        return false;
      }
      if (oldRun.getTime() !== run.getTime()) {
        return true;
      }
      if (oldRun.getResult() !== run.getResult()) {
        return true;
      }
      return false;
    };

    RunFeeder.prototype.discard = function(count) {
      var discarded, i, run, _i;
      if (count == null) {
        count = 1;
      }
      discarded = 0;
      if (count <= 0) {
        return 0;
      }
      for (i = _i = 1; 1 <= count ? _i <= count : _i >= count; i = 1 <= count ? ++_i : --_i) {
        run = this.strategy.popRun();
        this.runCount -= 1;
        if (run == null) {
          break;
        }
        discarded += 1;
      }
      return discarded;
    };

    RunFeeder.prototype.feed = function(count, callback) {
      var i, processed, run, _i;
      if (count == null) {
        count = 1;
      }
      if (callback == null) {
        callback = null;
      }
      processed = 0;
      if (count <= 0) {
        return 0;
      }
      for (i = _i = 1; 1 <= count ? _i <= count : _i >= count; i = 1 <= count ? ++_i : --_i) {
        run = this.strategy.popRun();
        if (run == null) {
          break;
        }
        this.contest.reflectRun(run);
        this.runCount -= 1;
        processed += 1;
        if (callback != null) {
          this.strategy.doCallback(callback, run);
        }
      }
      return processed;
    };

    RunFeeder.prototype.feedWhile = function(fnCriteria) {
      var processed, run;
      processed = 0;
      while (true) {
        run = this.strategy.front();
        if (run == null) {
          break;
        }
        if (fnCriteria(run)) {
          this.strategy.popRun();
          this.contest.reflectRun(run);
          this.runCount -= 1;
          processed += 1;
        } else {
          break;
        }
      }
      return processed;
    };

    RunFeeder.prototype.runDoEach = function(fn) {
      this.strategy.runDoEach(fn);
      return this;
    };

    return RunFeeder;

  })();

  AbstractRunFeedingStrategy = (function() {
    function AbstractRunFeedingStrategy() {}

    AbstractRunFeedingStrategy.prototype.selectRun = function() {
      throw new NotImplementedError();
    };

    AbstractRunFeedingStrategy.prototype.popRun = function() {
      throw new NotImplementedError();
    };

    AbstractRunFeedingStrategy.prototype.front = function() {
      throw new NotImplementedError();
    };

    AbstractRunFeedingStrategy.prototype.setContest = function(contest) {
      return this.contest = contest;
    };

    AbstractRunFeedingStrategy.prototype.runDoEach = function(fn) {
      throw new NotImplementedError();
    };

    AbstractRunFeedingStrategy.prototype.doCallback = function(callback, run) {
      return callback(run);
    };

    return AbstractRunFeedingStrategy;

  })();

  FIFORunFeedingStrategy = (function(_super) {
    __extends(FIFORunFeedingStrategy, _super);

    function FIFORunFeedingStrategy() {
      this.runPools = [];
    }

    FIFORunFeedingStrategy.prototype.popRun = function() {
      var run;
      run = this.runPools.shift();
      return run;
    };

    FIFORunFeedingStrategy.prototype.front = function(run) {
      return this.runPools[0];
    };

    FIFORunFeedingStrategy.prototype.pushRun = function(run) {
      return this.runPools.push(run);
    };

    FIFORunFeedingStrategy.prototype.runDoEach = function(fn) {
      var run, _i, _len, _ref;
      _ref = this.runPools;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        run = _ref[_i];
        fn(run);
      }
      return this;
    };

    return FIFORunFeedingStrategy;

  })(AbstractRunFeedingStrategy);

  TeamProblemSeparatedQueuedRunFeedingStrategy = (function(_super) {
    __extends(TeamProblemSeparatedQueuedRunFeedingStrategy, _super);

    function TeamProblemSeparatedQueuedRunFeedingStrategy(callbackFn) {
      this.callbackFn = callbackFn;
      this.runPools = {};
    }

    TeamProblemSeparatedQueuedRunFeedingStrategy.prototype.getFrontRunPool = function() {
      var callbackRetObj, pid, problem, runPool, team, tid;
      callbackRetObj = this.callbackFn();
      if (callbackRetObj === null) {
        return null;
      }
      pid = callbackRetObj.problemId;
      tid = callbackRetObj.teamId;
      if (pid === null && tid === null) {
        return null;
      }
      assert((this.contest != null) && this.contest instanceof Contest, "contest is not configured properly");
      if (tid == null) {
        throw new Error("invalid property teamId of the return value of the callback function");
      }
      if (pid == null) {
        throw new Error("invalid property problemId of the return value of the callback function");
      }
      problem = this.contest.getProblem(pid);
      team = this.contest.getTeam(tid);
      if (problem == null) {
        throw new Error("problem is invalidly chosen");
      }
      if (team == null) {
        throw new Error("team is invalidly chosen");
      }
      runPool = this.runPools[tid][pid];
      return runPool;
    };

    TeamProblemSeparatedQueuedRunFeedingStrategy.prototype.front = function() {
      var runPool;
      runPool = this.getFrontRunPool();
      return runPool[0];
    };

    TeamProblemSeparatedQueuedRunFeedingStrategy.prototype.popRun = function() {
      var run, runPool;
      runPool = this.getFrontRunPool();
      run = runPool.shift();
      return run;
    };

    TeamProblemSeparatedQueuedRunFeedingStrategy.prototype.doCallback = function(callback, run) {
      var rp;
      rp = this.runPools[run.getTeam().getId()][run.getProblem().getId()];
      return callback(run, rp.length);
    };

    TeamProblemSeparatedQueuedRunFeedingStrategy.prototype.setContest = function(contest) {
      var pid, problem, team, tid, _ref, _ref1;
      TeamProblemSeparatedQueuedRunFeedingStrategy.__super__.setContest.call(this, contest);
      assert(contest.getTeams() != null, "team is not configured");
      assert(contest.getProblems() != null, "problem is not configured");
      _ref = contest.getTeams();
      for (tid in _ref) {
        team = _ref[tid];
        this.runPools[team.getId()] = {};
        _ref1 = contest.getProblems();
        for (pid in _ref1) {
          problem = _ref1[pid];
          this.runPools[team.getId()][problem.getId()] = [];
        }
      }
      return this;
    };

    TeamProblemSeparatedQueuedRunFeedingStrategy.prototype.pushRun = function(run) {
      var pid, tid;
      assert(this.contest != null, "contest must be set properly");
      pid = run.getProblem().getId();
      tid = run.getTeam().getId();
      return this.runPools[tid][pid].push(run);
    };

    TeamProblemSeparatedQueuedRunFeedingStrategy.prototype.runDoEach = function(fn) {
      var pid, problem, rps, run, team, tid, _i, _len, _ref, _ref1;
      _ref = contest.getTeams();
      for (tid in _ref) {
        team = _ref[tid];
        _ref1 = contest.getProblems();
        for (pid in _ref1) {
          problem = _ref1[pid];
          rps = this.runPools[team.getId()][problem.getId()];
          for (_i = 0, _len = rps.length; _i < _len; _i++) {
            run = rps[_i];
            fn(run);
          }
        }
      }
      return this;
    };

    return TeamProblemSeparatedQueuedRunFeedingStrategy;

  })(AbstractRunFeedingStrategy);

  M = {
    Problem: Problem,
    Team: Team,
    Run: Run,
    Contest: Contest,
    TeamStatus: TeamStatus,
    TeamProblemStatus: TeamProblemStatus,
    ProblemSummary: ProblemSummary,
    RunFeeder: RunFeeder,
    FIFORunFeedingStrategy: FIFORunFeedingStrategy,
    TeamProblemSeparatedQueuedRunFeedingStrategy: TeamProblemSeparatedQueuedRunFeedingStrategy
  };

  $.extend(typeof exports !== "undefined" && exports !== null ? exports : this, M);

  return M;

}).call(this);
