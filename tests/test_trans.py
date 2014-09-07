import unittest

import numpy as np

from trans import (get_play, get_playtype, is_tod, MFLGraph,  _normalize_togo,
                   _normalize_yrd, set_to_on_downs, transition_matrix)
from utils import project_tuple


class TestGetPlay(unittest.TestCase):
    def raw2dict(self, raw):
        proj = project_tuple(4, 6, 7 ,8, 11)
        off, down, togo, ydline, desc = proj(raw.split(','))
        return {
            'off': off,
            'down': down,
            'togo': togo,
            'ydline': ydline,
            'description': desc,
        }
    def test_regular(self):
        raw = '''
            20130905_BAL@DEN,1,58,5,DEN,BAL,2,10,77,0,1,(13:05) (No Huddle Shotgun) K.Moreno right guard to DEN 24 for 1 yard (T.Suggs; J.Bynes).,0,-7,1,0,0,2013
        '''
        self.assertEqual(get_play(self.raw2dict(raw)),
                         {'atkr': 'DEN',
                          'down': '2',
                          'togo': '7',
                          'yrd': '2',
                          'playtype': 'regular'})

    def test_abs(self):
        raw = '''
            20130905_BAL@DEN,1,52,17,BAL,DEN,1,2,2,0,1,(7:17) J.Flacco pass short right to V.Leach for 2 yards TOUCHDOWN.,0,7,0,0,0,2013
        '''
        self.assertEqual(get_play(self.raw2dict(raw)),
                        {'atkr': 'BAL',
                         'down': '1',
                         'togo': '1',
                         'yrd': '9',
                         'playtype': 'td'})
        

class TestGetPlayType(unittest.TestCase):
    def test_punt(self):
        desc = '''
            (11:17) S.Koch punt is BLOCKED by D.Bruton Center-M.Cox recovered by BAL-S.Koch at BAL 10. S.Koch to BAL 10 for no gain (P.Lenon).
        '''
        self.assertEqual(get_playtype(desc), 'punt')

    def test_touchdown(self):
        desc = '''
            (7:17) J.Flacco pass short right to V.Leach for 2 yards TOUCHDOWN.
        '''
        self.assertEqual(get_playtype(desc), 'td')

    def test_field_goal(self):
        desc = '''
            (:10) J.Tucker 25 yard field goal is GOOD Center-M.Cox Holder-S.Koch.
        '''
        self.assertEqual(get_playtype(desc), 'fg')

    def test_safety(self):
        desc = '''
            (12:32) D.Colquitt punt is BLOCKED by J.Thomas Center-T.Gafford ball out of bounds in End Zone SAFETY.
        '''
        self.assertEqual(get_playtype(desc), 'safety')

    def test_fumble(self):
        desc = '''
            (14:27) P.Manning pass short right to E.Decker to BAL 28 for 27 yards (J.Smith). FUMBLES (J.Smith) ball out of bounds at BAL 28.
        '''
        self.assertEqual(get_playtype(desc), 'to')

    def test_int(self):
        desc = '''
            (12:13) (Shotgun) J.Flacco pass short right intended for R.Rice INTERCEPTED by D.Trevathan at BAL 30. D.Trevathan to BAL 1 for 29 yards. FUMBLES ball out of bounds in End Zone Touchback.
        '''
        self.assertEqual(get_playtype(desc), 'to')

    def test_regular(self):
        desc = '''
            (14:42) (No Huddle Shotgun) P.Manning pass short right to K.Moreno to DEN 21 for 8 yards (L.Webb).
        '''
        self.assertEqual(get_playtype(desc), 'regular')


class TestNormalizers(unittest.TestCase):
    def test_normalize_togo(self):
        self.assertEqual(_normalize_togo('15'), '10')

        self.assertEqual(_normalize_togo('10'), '7')
        self.assertEqual(_normalize_togo('7'), '7')

        self.assertEqual(_normalize_togo('5'), '5')
        self.assertEqual(_normalize_togo('6'), '5')

        self.assertEqual(_normalize_togo('3'), '3')
        self.assertEqual(_normalize_togo('4'), '3')

        self.assertEqual(_normalize_togo('1'), '1')
        self.assertEqual(_normalize_togo('2'), '1')

        self.assertEqual(_normalize_togo('0'), '0')

    def test_normalize_yrd(self):
        self.assertEqual(_normalize_yrd('100'), '0')
        self.assertEqual(_normalize_yrd('91'), '0')

        self.assertEqual(_normalize_yrd('90'), '1')
        self.assertEqual(_normalize_yrd('81'), '1')

        self.assertEqual(_normalize_yrd('69.5'), '3')
        self.assertEqual(_normalize_yrd('61.9'), '3')

        self.assertEqual(_normalize_yrd('60'), '4')
        self.assertEqual(_normalize_yrd('51'), '4')

        self.assertEqual(_normalize_yrd('50'), '5')
        self.assertEqual(_normalize_yrd('41'), '5')

        self.assertEqual(_normalize_yrd('10'), '9')
        self.assertEqual(_normalize_yrd('1'), '9')

        self.assertEqual(_normalize_yrd('0'), '10')


class TestSetTOonDowns(unittest.TestCase):
    def test_is_tod_4th_down_regular_no_next_play(self):
        p = {'playtype': 'regular',
             'down': '4',
             'togo': '5',
             'yrd': '8',
             'atkr': 'DAL'}
        self.assertTrue(is_tod(p, None))

    def test_is_tod_4th_down_abs_no_next_play(self):
        p = {'playtype': 'td',
             'down': '4',
             'togo': '5',
             'yrd': '8',
             'atkr': 'DAL'}
        self.assertFalse(is_tod(p, None))

    def test_is_tod_4th_down_abs_yes_next_play(self):
        p1 = {'playtype': 'td',
              'down': '4',
              'togo': '5',
              'yrd': '8',
              'atkr': 'DAL'}
        p2 = {'playtype': 'regular',
              'down': '1',
              'togo': '7',
              'yrd': '2',
              'atkr': 'WAS'}
        self.assertFalse(is_tod(p1, p2))

    def test_is_tod_4th_down_regular_yes_next_play(self):
        p1 = {'playtype': 'regular',
              'down': '4',
              'togo': '5',
              'yrd': '8',
              'atkr': 'DAL'}
        p2 = {'playtype': 'regular',
              'down': '1',
              'togo': '7',
              'yrd': '2',
              'atkr': 'WAS'}
        self.assertTrue(is_tod(p1, p2))

    def test_is_tod_4th_down_regular_yes_next_play_same_atkr(self):
        p1 = {'playtype': 'regular',
              'down': '4',
              'togo': '5',
              'yrd': '8',
              'atkr': 'DAL'}
        p2 = {'playtype': 'regular',
              'down': '1',
              'togo': '7',
              'yrd': '9',
              'atkr': 'DAL'}
        self.assertFalse(is_tod(p1, p2))

    def test_is_tod_3th_down_regular(self):
        p1 = {'playtype': 'regular',
              'down': '3',
              'togo': '5',
              'yrd': '8',
              'atkr': 'DAL'}
        p2 = {'playtype': 'regular',
              'down': '1',
              'togo': '7',
              'yrd': '9',
              'atkr': 'DAL'}
        self.assertFalse(is_tod(p1, p2))

    def test_set_to_on_down(self):
        atk1 = 'DAL'
        d = [
            {'playtype': 'regular',
             'down': '3',
             'togo': '5',
             'yrd': '8',
             'atkr': 'DAL'},

            {'playtype': 'regular',
             'down': '4',
             'togo': '5',
             'yrd': '8',
             'atkr': 'DAL'},

            # change of possession
            {'playtype': 'regular',
             'down': '1',
             'togo': '7',
             'yrd': '2',
             'atkr': 'WAS'},
        ]
        expected = [
            d[0].copy(),
            {'playtype': 'to',
             'down': '4',
             'togo': '5',
             'yrd': '8',
             'atkr': 'DAL'},
            d[2].copy(),
        ]
        self.assertEqual(set_to_on_downs(d), expected)

class TestMatrixStuff(unittest.TestCase):
    def assertMatrixEqual(self, got, expected):
        equality = got == expected
        if isinstance(equality, bool):
            return self.assertTrue(equality)
        else:
            msg = '\n' + str(equality)
            return self.assertTrue(equality.all(), msg)

    def test_transition_matrix(self):
        m = np.matrix([[2.0, 1.0],
                       [1.0, 0.0]])
        trans = transition_matrix(m)
        expected = np.matrix([[2.0/3.0, 1.0/3.0],
                              [1.0,         0.0]])
        self.assertMatrixEqual(trans, expected)


    def test_graph_to_matrix(self):
        plays = [
            {'playtype': 'regular', 'yrd': '3', 'togo': '7', 'down': '1'},
            {'playtype': 'regular', 'yrd': '3', 'togo': '3', 'down': '2'},
            {'playtype': 'to'},
        ]
        cis = MFLGraph(plays).to_matrix()
        expected = np.matrix([[0.0, 0.0, 0.0],  # still not hardcoded as 1.0
                              [1.0, 0.0, 0.0],
                              [0.0, 1.0, 0.0]])
        self.assertMatrixEqual(cis, expected)


if __name__ == '__main__':
    unittest.main()
