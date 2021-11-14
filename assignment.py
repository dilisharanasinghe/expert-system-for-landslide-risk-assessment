import time
from ui import Application
from emycin.emycin import Parameter, Context, Rule, Shell
import operator


def eq(x, y):
    return x == y


def boolean(string):
    if string == 'True':
        return True
    if string == 'False':
        return False
    raise ValueError('bool must be True or False')


def in_list(x, y):
    return x in y


def define_contexts(sh):
    sh.define_context(Context('land', ['district', 'ground-slop', 'has-building',
                                       'has-contour', 'dimension-perpendicular-to-contour',
                                       'soil-type', 'has-vertical-cut',
                                       'has-retaining-wall',
                                       'vertical-cut-height',
                                       'distance-from-house-to-vertical-cut'
                                       ]
                              ))

    sh.define_context(Context('regulatory-state',
                              goals=['suggestion', 'NBRO-approval']))


def define_params(sh):
    districts = ['ampara', 'anuradhapura', 'badulla', 'batticaloa', 'colombo', 'galle', 'gampaha', 'hambantota',
                 'jaffna', 'kalutara', 'kandy', 'kegalle', 'kilinochchi', 'kurunegala', 'mannar', 'matale',
                 'matara', 'monaragala', 'mullaitivu', 'nuwara eliya', 'polonnaruwa', 'puttalam', 'ratnapura',
                 'trincomalee', 'vavuniya']

    sh.define_param(Parameter('district', 'land', enum=districts, ask_first=True))
    sh.define_param(Parameter('ground-slop', 'land', cls=float, ask_first=True))

    sh.define_param(Parameter('vertical-cut-height', 'land', cls=float))
    sh.define_param(Parameter('distance-from-house-to-vertical-cut', 'land', cls=float))

    sh.define_param(Parameter('has-building', 'land', enum=['yes', 'no']))
    sh.define_param(Parameter('has-contour', 'land', enum=['yes', 'no']))
    sh.define_param(Parameter('has-vertical-cut', 'land', enum=['yes', 'no']))

    sh.define_param(Parameter('has-retaining-wall', 'land', enum=['yes', 'no']))
    sh.define_param(Parameter('dimension-perpendicular-to-contour', 'land', cls=float))
    sh.define_param(Parameter('soil-type', 'land', enum=['residual', 'colluvium']))

    sh.define_param(Parameter('suggestion', 'regulatory-state', cls=str))
    sh.define_param(Parameter('NBRO-approval', 'regulatory-state', enum=['needed', 'not-needed']))


def define_rules(sh):
    risky_districts = ['kalutara', 'matale', 'badulla', 'galle', 'hambantota', 'kandy', 'kegalle', 'matale',
                       'matara', 'nuwara eliya', 'ratnapura']

    # -------------- district and ground slop based approval ------------------------------------------------
    sh.define_rule(Rule(1,
                        [('ground-slop', 'land', lambda x, y: x < y, 11),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'not-needed'),
                         ],
                        0.55))

    sh.define_rule(Rule(2,
                        [('district', 'land', lambda x, y: x in y, risky_districts),
                         ('ground-slop', 'land', lambda x, y: x >= y, 11),
                         ('ground-slop', 'land', lambda x, y: x < y, 31),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ('suggestion', 'regulatory-state', eq,
                          "This district has been identified as landslide prone by NBRO")
                         ],
                        1.0))

    sh.define_rule(Rule(3,
                        [('district', 'land', lambda x, y: x not in y, risky_districts),
                         ('ground-slop', 'land', lambda x, y: x >= y, 11),
                         ('ground-slop', 'land', lambda x, y: x < y, 31),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'not-needed'),
                         ('suggestion', 'regulatory-state', eq,
                          "NBRO Guidelines to be strictly followed")
                         ],
                        0.65))

    sh.define_rule(Rule(4,
                        [('district', 'land', lambda x, y: x not in y, risky_districts),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'not-needed'),
                         ],
                        0.21))

    sh.define_rule(Rule(5,
                        [('district', 'land', lambda x, y: x in y, risky_districts),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ('suggestion', 'regulatory-state', eq,
                          "This district has been identified as landslide prone by NBRO")
                         ],
                        0.4))

    sh.define_rule(Rule(6,
                        [('ground-slop', 'land', lambda x, y: x >= y, 31)
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ('suggestion', 'regulatory-state', eq,
                          "Restriction on construction is mandatory, essential development activities need approval")
                         ],
                        1.0))

    sh.define_rule(Rule(7,
                        [('ground-slop', 'land', lambda x, y: x >= y, 11),
                         ('ground-slop', 'land', lambda x, y: x < y, 31),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ],
                        0.4))

    # ------------------ contour related -------------------------------------------------------------
    sh.define_rule(Rule(8,
                        [('has-contour', 'land', eq, 'yes'),
                         ('dimension-perpendicular-to-contour', 'land', lambda x, y: x < y, 5),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ],
                        0.4))

    sh.define_rule(Rule(9,
                        [('has-contour', 'land', eq, 'yes'),
                         ('has-building', 'land', eq, 'no')
                         ],
                        [('suggestion', 'regulatory-state', eq,
                          "Make building's longer side perpendicular to contour")],
                        0.8))

    sh.define_rule(Rule(10,
                        [('has-contour', 'land', eq, 'yes'),
                         ('dimension-perpendicular-to-contour', 'land', lambda x, y: x >= y, 5),
                         ('dimension-perpendicular-to-contour', 'land', lambda x, y: x < y, 7),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ('suggestion', 'regulatory-state', eq, 'An intermediate terrace of 0.6m can be implemented'),
                         ],
                        0.75))

    sh.define_rule(Rule(11,
                        [('has-contour', 'land', eq, 'yes'),
                         ('dimension-perpendicular-to-contour', 'land', lambda x, y: x >= y, 7),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ],
                        0.8))

    sh.define_rule(Rule(12,
                        [('has-contour', 'land', eq, 'yes'),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed')
                         ],
                        0.5))

    # ------------- vertical cut related -------------------------------------------------------------------

    sh.define_rule(Rule(13,
                        [('has-vertical-cut', 'land', eq, 'yes'),
                         ('has-retaining-wall', 'land', eq, 'no'),
                         ('vertical-cut-height', 'land', lambda x, y: x > y, 1.5),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ('suggestion', 'regulatory-state', eq, 'A retaining wall should be implemented'),
                         ],
                        0.85))

    sh.define_rule(Rule(14,
                        [('has-vertical-cut', 'land', eq, 'yes'),
                         ('has-retaining-wall', 'land', eq, 'no'),
                         ('soil-type', 'land', eq, 'residual'),
                         ('vertical-cut-height', 'land', lambda x, y: x > y, 1.5),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ('suggestion', 'regulatory-state', eq, 'A retaining wall should be implemented')
                         ],
                        0.75))

    sh.define_rule(Rule(15,
                        [('has-vertical-cut', 'land', eq, 'yes'),
                         ('has-retaining-wall', 'land', eq, 'no'),
                         ('soil-type', 'land', eq, 'colluvium'),
                         ('vertical-cut-height', 'land', lambda x, y: x > y, 1.0),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ('suggestion', 'regulatory-state', eq, 'A retaining wall should be implemented')
                         ],
                        0.8))

    sh.define_rule(Rule(16,
                        [('has-vertical-cut', 'land', eq, 'yes'),
                         ('distance-from-house-to-vertical-cut', 'land', lambda x, y: x < y, 2.0)],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ('suggestion', 'regulatory-state', eq,
                          'Minimum distance between house and the vertical cut not met')
                         ],
                        0.8))

    sh.define_rule(Rule(17,
                        [('has-vertical-cut', 'land', eq, 'yes'),
                         ('distance-from-house-to-vertical-cut', 'land', lambda x, y: x < y, 3.0),
                         ('ground-slop', 'land', lambda x, y: x >= y, 17)],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ('suggestion', 'regulatory-state', eq,
                          'Minimum distance between house and the vertical cut not met')
                         ],
                        0.82))

    sh.define_rule(Rule(18,
                        [('has-vertical-cut', 'land', eq, 'yes'),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ],
                        0.6))

    sh.define_rule(Rule(19,
                        [('has-vertical-cut', 'land', eq, 'yes'),
                         ('vertical-cut-height', 'land', lambda x, y: x > y, 1.0),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ],
                        0.7))

    sh.define_rule(Rule(20,
                        [('has-vertical-cut', 'land', eq, 'yes'),
                         ('has-retaining-wall', 'land', eq, 'no'),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ('suggestion', 'regulatory-state', eq, 'A retaining wall should be implemented')
                         ],
                        0.65))

    sh.define_rule(Rule(21,
                        [('has-vertical-cut', 'land', eq, 'yes'),
                         ('has-retaining-wall', 'land', eq, 'no'),
                         ('ground-slop', 'land', lambda x, y: x >= y, 11),
                         ('ground-slop', 'land', lambda x, y: x < y, 31),
                         ],
                        [('suggestion', 'regulatory-state', eq, 'Retaining wall should designed by a technically '
                                                                'qualified person')
                         ],
                        0.7))

    sh.define_rule(Rule(22,
                        [('has-vertical-cut', 'land', eq, 'yes'),
                         ('has-retaining-wall', 'land', eq, 'yes'),
                         ],
                        [('NBRO-approval', 'regulatory-state', eq, 'not-needed'),
                         ],
                        0.35))

    sh.define_rule(Rule(23,
                        [('has-vertical-cut', 'land', eq, 'yes'),
                         ],
                        [('suggestion', 'regulatory-state', eq, 'Minimum horizontal distance to the nearest building '
                                                                'from the top of the vertical cut has to be > Height of'
                                                                ' the cut'),
                         ],
                        0.8))

    # ---------- deducible items -----------------------------------------------------------
    sh.define_rule(Rule(24,
                        [('has-vertical-cut', 'land', eq, 'no'),
                         ],
                        [('has-retaining-wall', 'land', eq, 'no'),
                         ('vertical-cut-height', 'land', eq, 0),
                         ('distance-from-house-to-vertical-cut', 'land', lambda x, y: x > y, 100.0),
                         ],
                        1.0))

    sh.define_rule(Rule(25,
                        [('has-building', 'land', eq, 'no'),
                         ],
                        [('distance-from-house-to-vertical-cut', 'land', lambda x, y: x > y, 100.0),
                         ],
                        1.0))

    sh.define_rule(Rule(26,
                        [('has-contour', 'land', eq, 'no'),
                         ],
                        [('dimension-perpendicular-to-contour', 'land', lambda x, y: x < y, 5),
                         ],
                        1.0))


    # -------- house already exist ----------------------------------------------------------------

    sh.define_rule(Rule(27,
                        [('has-building', 'land', eq, 'yes'),
                         ('NBRO-approval', 'regulatory-state', eq, 'needed'),
                         ],
                        [('suggestion', 'regulatory-state', eq,
                          'Development of surface drainage is Mandatory'),
                         ],
                        1.0))

    sh.define_rule(Rule(28,
                        [('has-building', 'land', eq, 'yes'),
                         ('ground-slop', 'land', lambda x, y: x >= y, 11),
                         ('ground-slop', 'land', lambda x, y: x < y, 31)
                         ],
                        [('suggestion', 'regulatory-state', eq,
                          'Development of surface drainage is Mandatory'),
                         ],
                        0.7))

    sh.define_rule(Rule(29,
                        [('ground-slop', 'land', lambda x, y: x >= y, 11),
                         ('ground-slop', 'land', lambda x, y: x < y, 31)
                         ],
                        [('suggestion', 'regulatory-state', eq,
                          'Turf or other erosion control measures are recommended'),
                         ],
                        0.8))

    # --------- soil ----------------------------------------------------------
    sh.define_rule(Rule(30,
                        [('soil-type', 'land', eq, 'colluvium'),
                         ],
                        [('suggestion', 'regulatory-state', eq,
                          'Unsupported vertical cuts in this soil are not encouraged'),
                         ],
                        0.9))


def report_findings(findings, sh):
    output = ''
    print(findings)
    # for inst, result in findings.items():
    #     for param, vals in result.items():
    #         possibilities = ['%s: %.2f' % (val[0], val[1]) for val in vals.items()]
    #         output += '%s: %s\n' % (param, ', '.join(possibilities))

    results = findings.values()[0]
    nbro_approval = results['NBRO-approval']
    sorted_x = sorted(nbro_approval.items(), key=operator.itemgetter(1), reverse=True)
    total_prob_x = 0.0
    for i in sorted_x:
        total_prob_x += i[1]
    # print(total_prob_x)

    suggestions = results['suggestion']
    sorted_y = sorted(suggestions.items(), key=operator.itemgetter(1), reverse=True)
    total_prob_y = 0.0
    for i in sorted_y:
        total_prob_y += i[1]
    # print(total_prob_y)

    # print(findings, sorted_x)

    approval_string = ''
    for item in sorted_x:
        approval_string += '{0:<20} : {1:.2f}\n'.format(item[0], item[1]/total_prob_x)

    suggestions_string = ''
    for item in sorted_y:
        suggestions_string += '{0:<60} : {1:.2f}\n'.format(item[0], item[1]/total_prob_y)

    sh.ui.set_approval_state(approval_string)
    sh.ui.set_suggestions(suggestions_string)
    # sh.ui.set_output(output)


reset_flag = False


def reset_callback():
    global reset_flag
    reset_flag = True


def main():
    global reset_flag
    user_interface = Application(reset_callback=reset_callback)
    user_interface.run()
    time.sleep(1.0)

    while True:
        reset_flag = False
        print('--------------------------- Execution started ------------------------------------')
        sh = Shell(ui=user_interface)
        define_contexts(sh)
        define_params(sh)
        define_rules(sh)
        report_findings(sh.execute(['land', 'regulatory-state']), sh)

        while not reset_flag:
            time.sleep(0.5)


if __name__ == '__main__':
    main()
