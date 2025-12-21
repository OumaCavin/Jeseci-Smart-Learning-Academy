import {__jacJsx, __jacSpawn} from "@jac-client/utils";
import { jacSpawn, jacLogin, jacSignup, jacLogout, jacIsLoggedIn, navigate, Link, useRouter } from "@jac-client/utils";
function LearningDashboard() {
  return __jacJsx("div", {"style": containerStyle}, [__jacJsx("div", {"style": headerStyle}, [__jacJsx("h1", {"style": titleStyle}, ["Jeseci Smart Learning Academy"]), __jacJsx("p", {"style": subtitleStyle}, ["Pure Jaclang 0.9.3 Architecture"])]), __jacJsx("div", {"style": cardStyle}, [__jacJsx("h2", {"style": h2Style}, ["Application Status: Operational"]), __jacJsx("p", {}, [__jacJsx("strong", {}, ["Version:"]), " 5.0.0"]), __jacJsx("p", {}, [__jacJsx("strong", {}, ["Architecture:"]), " Pure Jaclang + Native JSX"]), __jacJsx("p", {}, [__jacJsx("strong", {}, ["Backend:"]), " Object-Spatial Programming APIs"]), __jacJsx("p", {}, [__jacJsx("strong", {}, ["Frontend:"]), " Built-in React-like Components"])]), __jacJsx("div", {"style": gridStyle}, [__jacJsx("div", {"style": apiCardStyle}, [__jacJsx("h3", {}, ["Backend APIs"]), __jacJsx("p", {}, ["Native Jac Walkers with Object-Spatial Programming"]), __jacJsx("button", {"style": buttonStyle, "onClick": () => {
    testWelcomeAPI();
  }}, ["Test Welcome API"]), __jacJsx("button", {"style": buttonBlueStyle, "onClick": () => {
    testHealthAPI();
  }}, ["Health Check"]), __jacJsx("button", {"style": buttonOrangeStyle, "onClick": () => {
    testConceptsAPI();
  }}, ["View Concepts"]), __jacJsx("button", {"style": buttonPurpleStyle, "onClick": () => {
    testProgressAPI();
  }}, ["User Progress"])]), __jacJsx("div", {"style": infoCardStyle}, [__jacJsx("h3", {}, ["🔧 Architecture Benefits"]), __jacJsx("ul", {}, [__jacJsx("li", {}, ["Single language (Jaclang)"]), __jacJsx("li", {}, ["No external React dependencies"]), __jacJsx("li", {}, ["Native JSX implementation"]), __jacJsx("li", {}, ["Built-in authentication"]), __jacJsx("li", {}, ["Native backend communication"]), __jacJsx("li", {}, ["Zero configuration build"])])])]), __jacJsx("div", {"style": footerStyle}, [__jacJsx("p", {}, ["Built with Jaclang 0.9.3 Object-Spatial Programming"]), __jacJsx("p", {}, ["© 2025 Cavin Otieno • Jeseci Smart Learning Academy"])])]);
}
function testWelcomeAPI() {
  alert("Testing Welcome API - Check browser console for actual response");
  console.log("Would call: jacSpawn('init', '', {})");
}
function testHealthAPI() {
  alert("Testing Health Check API - Check browser console for actual response");
  console.log("Would call: jacSpawn('health_check', '', {})");
}
function testConceptsAPI() {
  alert("Testing Concepts API - Check browser console for actual response");
  console.log("Would call: jacSpawn('concepts', '', {})");
}
function testProgressAPI() {
  alert("Testing Progress API - Check browser console for actual response");
  console.log("Would call: jacSpawn('user_progress', '', {})");
}
function app() {
  return __jacJsx(LearningDashboard, {}, []);
}
export { LearningDashboard, app, testConceptsAPI, testHealthAPI, testProgressAPI, testWelcomeAPI };
