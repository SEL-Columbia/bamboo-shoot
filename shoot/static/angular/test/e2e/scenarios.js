'use strict';

/* http://docs.angularjs.org/guide/dev_guide.e2e-testing */

describe('my app', function() {

  beforeEach(function() {
    browser().navigateTo('../../app/index.html');
  });


  it('should automatically redirect to /view1 when location hash/fragment is empty', function() {
    expect(browser().location().url()).toBe("/view1");
  });


  describe('view1', function() {

    beforeEach(function() {
      browser().navigateTo('#/view1');
    });


    it('should render view1 when user navigates to /view1', function() {
      expect(element('[ng-view] p:first').text()).
        toMatch(/partial for view 1/);
    });

    it('should hide the tusker question if client doesnt drink', function(){
       expect(element('[ng-view] p.is-drinker:visible').count()).toEqual(0);
    });

  });


  describe('view2', function() {

    beforeEach(function() {
      browser().navigateTo('#/view2');
    });


    it('should render view2 when user navigates to /view2', function() {
      expect(element('[ng-view] p:first').text()).
        toMatch(/partial for view 2/);
    });

  });
});

describe("not an angular app", function () {
    beforeEach(function () {
        browser().navigateTo("../../app/non-angular.html")
    });

    it("should add a list item on click", function () {
        element('a.add-to-list').click();
        expect(element('ul.nav li').count()).toEqual(2);
    });
});
