import { FallbackActivity, ActivityProps} from '../../components/Activity';

function Login(props: ActivityProps) {
    return FallbackActivity(props);
}

function Register(props: ActivityProps) {
    return FallbackActivity(props);
}

function Logout(props: ActivityProps) {
    return FallbackActivity(props);
}

export default {
    "profile.auth.login": Login,
    "profile.auth.register": Register,
    "profile.auth.logout": Logout,
};
