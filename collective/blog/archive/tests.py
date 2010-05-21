import os
import unittest
from datetime import datetime

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.Five import testbrowser
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite(products=['collective.blog.archive'])

import collective.blog.archive

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.blog.archive)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass
        
class FunctionalTestCase(ptc.FunctionalTestCase, TestCase):
    
    def test_archive(self):
        # Use a browser to log into the portal:
        admin = testbrowser.Browser()
        admin.handleErrors = False
        portal_url = self.portal.absolute_url()
        admin.open(portal_url)
        admin.getControl(name='__ac_name').value = ptc.portal_owner
        admin.getControl(name='__ac_password').value = ptc.default_password
        admin.getControl('Log in').click()

        # Create a folder to act as the blog:
        admin.getLink(id='folder').click()
        admin.getControl(name='title').value = 'A Blog'
        admin.getControl(name='form.button.save').click()
        # Publish it:
        admin.getLink(id='workflow-transition-publish').click()
        # Save this url for easy access later:
        blog_url = admin.url
        
        # Add the portlet:
        admin.getLink('Manage portlets').click()
        self.assert_('Monthly archive portlet' in admin.contents)
        admin.open(blog_url + '/++contextportlets++plone.rightcolumn/+/collective.blog.archive.portlet')
        
        # In the folder, create content with a varying set of publishing dates.
        dates = [datetime(2008, 2, 29, 8, 0), datetime(2008, 5, 7, 00, 0),
                 datetime(2009, 7, 9, 12, 0), datetime(2010, 1, 3, 12, 0),
                 datetime(2010, 1, 5, 12, 0), datetime(2010, 1, 7, 12, 0),
                 datetime(2010, 2, 3, 12, 0), datetime(2010, 2, 23, 12, 0),
                 datetime(2010, 3, 29, 23, 20), datetime(2010, 4, 2, 12, 0),
                 datetime(2010, 5, 21, 12, 0)]
        
        for date in dates:
            admin.open(blog_url)
            admin.getLink(id='document').click()
            admin.getControl(name='title').value = 'Blog Entry for %s' % date.strftime('%Y-%m-%d %H:%M')
            admin.getControl(name='text').value = 'The main body of the Document'
            admin.getControl(name='effectiveDate_year').value = [date.strftime('%Y')]
            admin.getControl(name='effectiveDate_month').value = [date.strftime('%m')]
            admin.getControl(name='effectiveDate_day').value = [date.strftime('%d')]
            admin.getControl(name='effectiveDate_hour').value = [date.strftime('%I')]
            admin.getControl(name='effectiveDate_minute').value = [date.strftime('%M')]
            admin.getControl(name='effectiveDate_ampm').value = [date.strftime('%p')]
            admin.getControl(name='form.button.save').click()
            admin.getLink(id='workflow-transition-publish').click()
            
        # Check that the portlet works:
        admin.open(blog_url)
        portlet = admin.contents[admin.contents.find('<dl class="portlet portletArchivePortlet">'):]
        portlet = portlet[:portlet.find('</dl>')]
        
        # The test of the portlet content is ugly. Maybe it could be made
        # prettier by looking at the code as XML...
        pos = portlet.find('2008')
        self.assert_(pos != -1)
        pos = portlet.find('month_2', pos)
        self.assert_(pos != -1)
        pos = portlet.find('(1)', pos)
        self.assert_(pos != -1)
        pos = portlet.find('month_5', pos)
        self.assert_(pos != -1)
        pos = portlet.find('(1)', pos)
        self.assert_(pos != -1)
        pos = portlet.find('2009', pos)                         
        self.assert_(pos != -1)
        pos = portlet.find('month_7', pos)
        self.assert_(pos != -1)
        pos = portlet.find('(1)', pos)
        self.assert_(pos != -1)
        pos = portlet.find('2010', pos)
        self.assert_(pos != -1)
        pos = portlet.find('month_1', pos)
        self.assert_(pos != -1)
        pos = portlet.find('(3)', pos)
        self.assert_(pos != -1)
        pos = portlet.find('month_2', pos)
        self.assert_(pos != -1)
        pos = portlet.find('(2)', pos)
        self.assert_(pos != -1)
        pos = portlet.find('month_3', pos)        
        self.assert_(pos != -1)
        pos = portlet.find('(1)', pos)        
        self.assert_(pos != -1)
        pos = portlet.find('month_4', pos)
        self.assert_(pos != -1)
        pos = portlet.find('(1)', pos)
        self.assert_(pos != -1)
        pos = portlet.find('month_5', pos)
        self.assert_(pos != -1)
        pos = portlet.find('(1)', pos)
        self.assert_(pos != -1)
        
def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(FunctionalTestCase),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
